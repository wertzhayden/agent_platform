"""DEFAULT UTILITY METHODS USED TO HELP WEBSCRAPERS"""
from webscraper.constants.headers_for_player_stats import wr_career_stats_headers, wr_game_stats_headers, rb_career_stats_headers, rb_game_stats_headers


def determine_ourlads_headers_by_position(position: str) -> tuple[list[str], list[str]]:
    """
    If the Player is a RB --> Use RB Headers
    If the Player is a WR or TE --> Use WR Headers
    Otherwise, use default Ourlads headers
    """
    if not position:
        return [], []
    position = position.upper()
    if 'RB' in position or "FB" in position:
        return rb_career_stats_headers, rb_game_stats_headers
    if 'WR' in position or 'TE' in position:
        return wr_career_stats_headers, wr_game_stats_headers
    