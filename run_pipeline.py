from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timedelta


def run_step(name: str, command: list[str]) -> None:
    banner = f"🔧 Executando: {name}"
    print(banner)
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"❌ Falha em '{name}'. Código de saída: {exc.returncode}")
        sys.exit(exc.returncode or 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline completo Taze AI (ingest + train + inference)")
    parser.add_argument(
        "--skip-train",
        action="store_true",
        help="Pula a etapa de treinamento (útil para testes rápidos).",
    )
    args = parser.parse_args()

    print("🚀 Iniciando pipeline Taze AI\n")

    # Step 1: Ingest
    run_step("Ingestão de dados", [sys.executable, "-m", "ml.ingest"])

    # Step 2: Train
    if args.skip_train:
        print("⏭️  Treinamento ignorado por --skip-train\n")
    else:
        train_until = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        run_step(
            f"Treinamento (train_until={train_until})",
            [sys.executable, "-m", "ml.train_buyhold", "--train-until", train_until],
        )

    # Step 3: Inference
    run_step("Inferência / geração de sinais", [sys.executable, "-m", "ml.inference"])

    print("\n✅ Pipeline concluído com sucesso! Acesse http://localhost:3000/admin para validar.")


if __name__ == "__main__":
    main()
