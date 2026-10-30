import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ENTRADAS_DIR = BASE_DIR / "entradas"
SAIDAS_DIR = BASE_DIR / "saidas"


# ------------------------------------------------------------
# ESCOLHA DO CONJUNTO
# ------------------------------------------------------------

# INPUT_SET = "portugues_acentuado"
INPUT_SET = "portugues_sem_acento"
# INPUT_SET = "ingles"

# Para executar TODOS:
#
# INPUT_SET = None


# ------------------------------------------------------------
# CONFIGURAÇÃO DO SCANNER
# ------------------------------------------------------------

ANALYZERS = "llm"

OUTPUT_FORMAT = "raw"

LLM_MODEL = "gemini/gemini-3.1-flash-lite"

LLM_TIMEOUT = "120"

PROCESS_TIMEOUT = 1800


# ============================================================
# AMBIENTE
# ============================================================

def configurar_ambiente():

    env = os.environ.copy()

    api_key = env.get("MCP_SCANNER_LLM_API_KEY")

    if not api_key:

        raise RuntimeError(
            "\n"
            "A variável MCP_SCANNER_LLM_API_KEY não foi encontrada.\n\n"
            "Execute no PowerShell:\n\n"
            '$env:MCP_SCANNER_LLM_API_KEY="SUA_CHAVE"\n'
        )

    env["MCP_SCANNER_LLM_API_KEY"] = api_key

    env["MCP_SCANNER_LLM_MODEL"] = LLM_MODEL

    env["MCP_SCANNER_LLM_TIMEOUT"] = LLM_TIMEOUT

    # Não utilizar configuração antiga do Ollama.
    env.pop(
        "MCP_SCANNER_LLM_BASE_URL",
        None
    )

    return env


# ============================================================
# DATASETS
# ============================================================

def encontrar_datasets(pasta):

    return sorted(
        arquivo
        for arquivo in pasta.iterdir()
        if arquivo.is_file()
        and arquivo.suffix.lower() == ".json"
    )


# ============================================================
# EXECUÇÃO DO SCANNER
# ============================================================

def executar_scanner(
    dataset,
    arquivo_saida,
    arquivo_log,
    env
):

    server_path = BASE_DIR / "server.py"

    # IMPORTANTE:
    #
    # Não usar:
    #
    # --stdio-args "server.py --dataset ..."
    #
    # porque nessa versão do scanner isso vira
    # um único argumento.
    #
    # Usamos --stdio-arg separadamente.

    comando = [

        "mcp-scanner",

        "--analyzers",
        ANALYZERS,

        "--format",
        OUTPUT_FORMAT,

        "stdio",

        "--stdio-command",
        sys.executable,

        "--stdio-arg",
        str(server_path),

        "--stdio-arg=--dataset",

        "--stdio-arg",
        str(dataset.resolve())
    ]

    print()
    print("=" * 70)

    print(
        f"Executando: {dataset.name}"
    )

    print(
        f"Entrada:   {dataset}"
    )

    print(
        f"Saída:     {arquivo_saida}"
    )

    print(
        "Comando:"
    )

    print(
        " ".join(f'"{x}"' if " " in x else x for x in comando)
    )

    print("=" * 70)

    inicio = datetime.now()

    try:

        processo = subprocess.run(

            comando,

            cwd=BASE_DIR,

            env=env,

            capture_output=True,

            text=True,

            encoding="utf-8",

            errors="replace",

            timeout=PROCESS_TIMEOUT
        )

        fim = datetime.now()

        duracao = (
            fim - inicio
        ).total_seconds()

        # ----------------------------------------------------
        # SALVA STDOUT
        # ----------------------------------------------------

        arquivo_saida.write_text(
            processo.stdout or "",
            encoding="utf-8"
        )

        # ----------------------------------------------------
        # SALVA STDERR
        # ----------------------------------------------------

        arquivo_log.write_text(
            processo.stderr or "",
            encoding="utf-8"
        )

        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        if processo.returncode == 0:

            print(
                f"[OK] Concluído em {duracao:.1f}s"
            )

        else:

            print(
                f"[ERRO] Código de saída: "
                f"{processo.returncode}"
            )

            print(
                f"Veja o log: {arquivo_log}"
            )

        return processo.returncode

    except subprocess.TimeoutExpired as erro:

        print(
            "[TIMEOUT] O processo excedeu "
            f"{PROCESS_TIMEOUT} segundos."
        )

        stdout = erro.stdout or ""
        stderr = erro.stderr or ""

        if isinstance(stdout, bytes):

            stdout = stdout.decode(
                "utf-8",
                errors="replace"
            )

        if isinstance(stderr, bytes):

            stderr = stderr.decode(
                "utf-8",
                errors="replace"
            )

        arquivo_saida.write_text(
            stdout,
            encoding="utf-8"
        )

        arquivo_log.write_text(
            stderr
            + "\n\n"
            + "PROCESSO ENCERRADO POR TIMEOUT.\n",
            encoding="utf-8"
        )

        return -1


# ============================================================
# EXECUTA UM CONJUNTO
# ============================================================

def executar_conjunto(
    pasta_entrada,
    env
):

    pasta_saida = (
        SAIDAS_DIR
        / pasta_entrada.name
    )

    pasta_saida.mkdir(
        parents=True,
        exist_ok=True
    )

    datasets = encontrar_datasets(
        pasta_entrada
    )

    if not datasets:

        print(
            f"[AVISO] Nenhum JSON em "
            f"{pasta_entrada}"
        )

        return 0, 0

    executados = 0
    erros = 0

    print()
    print(
        f"### CONJUNTO: "
        f"{pasta_entrada.name}"
    )

    print(
        f"Datasets encontrados: "
        f"{len(datasets)}"
    )

    for dataset in datasets:

        horario = datetime.now().strftime("%H-%M-%S")

        arquivo_saida = (
            pasta_saida
            / f"{dataset.stem}_{horario}.json"
        )

        arquivo_log = (
            pasta_saida
            / f"{dataset.stem}_{horario}.log"
        )

        codigo = executar_scanner(

            dataset=dataset,

            arquivo_saida=arquivo_saida,

            arquivo_log=arquivo_log,

            env=env
        )

        executados += 1

        if codigo != 0:

            erros += 1

    return executados, erros


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("MCP TOOL POISONING - TESTE AUTOMATIZADO")
    print("=" * 70)

    print(
        f"Modelo:      {LLM_MODEL}"
    )

    print(
        f"Analisador:  {ANALYZERS}"
    )

    print(
        f"Entradas:    {ENTRADAS_DIR}"
    )

    print(
        f"Saídas:      {SAIDAS_DIR}"
    )

    print("=" * 70)

    env = configurar_ambiente()

    if INPUT_SET is None:

        pastas = sorted(
            pasta
            for pasta in ENTRADAS_DIR.iterdir()
            if pasta.is_dir()
        )

    else:

        pasta = (
            ENTRADAS_DIR
            / INPUT_SET
        )

        if not pasta.exists():

            raise FileNotFoundError(
                f"\nPasta não encontrada:\n"
                f"{pasta}"
            )

        pastas = [pasta]

    total = 0
    erros = 0

    for pasta in pastas:

        executados, falhas = (
            executar_conjunto(
                pasta,
                env
            )
        )

        total += executados
        erros += falhas

    print()
    print("=" * 70)
    print("EXECUÇÃO FINALIZADA")
    print("=" * 70)

    print(
        f"Datasets executados: {total}"
    )

    print(
        f"Falhas/timeouts:     {erros}"
    )

    print("=" * 70)


if __name__ == "__main__":

    main()