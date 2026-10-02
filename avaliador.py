
import json
from pathlib import Path
from collections import Counter


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

SAIDAS_DIR = BASE_DIR / "saidas"


def carregar_json(caminho):

    try:

        with caminho.open(
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(arquivo)

    except Exception as erro:

        print()
        print(
            f"[ERRO] Não foi possível ler:"
        )

        print(caminho)

        print(
            f"Motivo: {erro}"
        )

        return None


# ============================================================
# EXTRAÇÃO DOS RESULTADOS
# ============================================================

def encontrar_resultados(data):
    """
    Obtém a lista scan_results do formato RAW
    produzido pelo MCP Scanner.
    """

    if not isinstance(data, dict):

        return []

    resultados = data.get(
        "scan_results"
    )

    if isinstance(resultados, list):

        return resultados

    return []


# ============================================================
# OBTÉM RESULTADO DO LLM
# ============================================================

def obter_llm_analyzer(resultado):
    """
    Obtém o resultado produzido pelo llm_analyzer.

    Estrutura esperada:

    scan_results
        └── findings
            └── llm_analyzer
    """

    findings = resultado.get(
        "findings",
        {}
    )

    if not isinstance(findings, dict):

        return {}

    llm = findings.get(
        "llm_analyzer",
        {}
    )

    if not isinstance(llm, dict):

        return {}

    return llm


# ============================================================
# ANÁLISE
# ============================================================

def analisar_dataset(caminho):

    data = carregar_json(
        caminho
    )

    if data is None:

        return None

    resultados = encontrar_resultados(
        data
    )

    total_safe = 0
    total_maliciosos = 0
    total_findings = 0

    tipos_ameacas = Counter()

    ferramentas_analisadas = 0

    for resultado in resultados:

        if not isinstance(
            resultado,
            dict
        ):

            continue

        ferramentas_analisadas += 1



        is_safe = resultado.get(
            "is_safe"
        )


        llm = obter_llm_analyzer(
            resultado
        )

        threat_names = llm.get(
            "threat_names",
            []
        )

        findings = llm.get(
            "total_findings",
            0
        )



        if (
            is_safe is True
            and not threat_names
        ):

            total_safe += 1


        elif threat_names:

            total_maliciosos += 1

            for threat in threat_names:

                tipos_ameacas[threat] += 1



        if isinstance(
            findings,
            int
        ):

            total_findings += findings

    return {

        "arquivo": caminho.name,

        "ferramentas_analisadas":
            ferramentas_analisadas,

        "total_safe":
            total_safe,

        "total_maliciosos":
            total_maliciosos,

        "total_findings":
            total_findings,

        "tipos_ameacas":
            tipos_ameacas
    }



def exibir_resultado(resultado):

    print()
    print("=" * 60)

    print(
        "RESULTADO"
    )

    print("=" * 60)

    print()

    print(
        f"Dataset: "
        f"{resultado['arquivo']}"
    )

    print(
        f"Descrições analisadas: "
        f"{resultado['ferramentas_analisadas']}"
    )

    print()

    print(
        f"SAFE: "
        f"{resultado['total_safe']}"
    )

    print()

    print(
        "MALICIOSOS POR TIPO:"
    )

    if resultado["tipos_ameacas"]:

        for tipo, quantidade in sorted(
            resultado["tipos_ameacas"].items()
        ):

            print(
                f"  {tipo:<25} "
                f"{quantidade}"
            )

    else:

        print(
            "  Nenhuma ameaça encontrada."
        )

    print()

    print(
        f"TOTAL MALICIOSOS: "
        f"{resultado['total_maliciosos']}"
    )

    print(
        f"TOTAL FINDINGS:   "
        f"{resultado['total_findings']}"
    )

    print()

    print("=" * 60)



def encontrar_conjuntos():

    if not SAIDAS_DIR.exists():

        return []

    return sorted(
        pasta
        for pasta in SAIDAS_DIR.iterdir()
        if pasta.is_dir()
    )


# ============================================================
# JSONS
# ============================================================

def encontrar_jsons(pasta):

    return sorted(
        arquivo
        for arquivo in pasta.iterdir()
        if arquivo.is_file()
        and arquivo.suffix.lower() == ".json"
    )


# ============================================================
# MENU DE DATASETS
# ============================================================

def menu_datasets(pasta):

    while True:

        datasets = encontrar_jsons(
            pasta
        )

        print()
        print("=" * 60)

        print(
            f"CONJUNTO: "
            f"{pasta.name}"
        )

        print("=" * 60)

        if not datasets:

            print()

            print(
                "Nenhum JSON encontrado."
            )

            input(
                "\nPressione ENTER para voltar..."
            )

            return

        print()

        for indice, dataset in enumerate(
            datasets,
            start=1
        ):

            print(
                f"{indice}. "
                f"{dataset.name}"
            )

        print()

        print(
            "0. Voltar"
        )

        print()

        escolha = input(
            "Escolha: "
        ).strip()

        if escolha == "0":

            return

        try:

            indice = int(
                escolha
            )

        except ValueError:

            print(
                "\n[ERRO] Opção inválida."
            )

            continue

        if not (
            1 <= indice <= len(datasets)
        ):

            print(
                "\n[ERRO] Opção inválida."
            )

            continue

        dataset = datasets[
            indice - 1
        ]

        resultado = analisar_dataset(
            dataset
        )

        if resultado is not None:

            exibir_resultado(
                resultado
            )

            input(
                "\nPressione ENTER para continuar..."
            )


def menu_principal():

    while True:

        conjuntos = encontrar_conjuntos()

        print()
        print("=" * 60)

        print(
            "MCP TOOL POISONING - ANALISADOR"
        )

        print("=" * 60)

        print()

        if not conjuntos:

            print(
                "Nenhum conjunto encontrado em:"
            )

            print(
                SAIDAS_DIR
            )

            return

        print(
            "Conjuntos disponíveis:"
        )

        print()

        for indice, pasta in enumerate(
            conjuntos,
            start=1
        ):

            print(
                f"{indice}. "
                f"{pasta.name}"
            )

        print()

        print(
            "0. Sair"
        )

        print()

        escolha = input(
            "Escolha: "
        ).strip()

        if escolha == "0":

            print()

            print(
                "Encerrando..."
            )

            return

        try:

            indice = int(
                escolha
            )

        except ValueError:

            print(
                "\n[ERRO] Opção inválida."
            )

            continue

        if not (
            1 <= indice <= len(conjuntos)
        ):

            print(
                "\n[ERRO] Opção inválida."
            )

            continue

        menu_datasets(
            conjuntos[
                indice - 1
            ]
        )


if __name__ == "__main__":

    menu_principal()

