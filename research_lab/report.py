"""Compact research summary formatter."""


def build_summary(*, learned: str, improved: str, numbers: str, decision: str,
                  maturity: str, next_theme: str, github_update: bool) -> str:
    update = "必要" if github_update else "不要"
    return "\n".join([
        "研究サマリー",
        f"学習: {learned}",
        f"改善: {improved}",
        f"重要数値: {numbers}",
        f"判断: {decision}",
        f"成熟度: {maturity}",
        f"次の研究: {next_theme}",
        f"GitHub main更新: {update}",
    ])
