from dataforge.orchestration.cli import build_parser


def test_orchestration_cli_parser():
    parser = build_parser()
    args = parser.parse_args(["run", "--input", "input", "--output", "output"])
    assert args.command == "run"
    assert args.input == "input"
    assert args.output == "output"
    assert args.log_level == "INFO"
