from dataforge.cli import build_parser


def test_cli_parser_requires_input_and_output():
    parser = build_parser()
    args = parser.parse_args(["run", "--input", "in", "--output", "out"])
    assert args.command == "run"
    assert args.input == "in"
    assert args.output == "out"
    assert args.log_level == "WARNING"
