# from collections import defaultdict, OrderedDict
# from functools import cmp_to_key
# from typing import Dict, Tuple, List, Any

# from rest_framework import viewsets
# from rest_framework.response import Response
# from core.models.active_nfl_players import ActiveNFLPlayers

# from webscraper.constants.ourlads_constants import TEAM_IDS


# def sort_rounds(rounds_dict):
#     desired_order = [f"round_{i}" for i in range(1, 8)] + ["round_undrafted"]
#     return OrderedDict((key, rounds_dict[key]) for key in desired_order if key in rounds_dict)


# def parse_draft_pick(pick):
#     if isinstance(pick, str) and pick.lower() == "undrafted":
#         return float("inf")
#     try:
#         return int(pick)
#     except (TypeError, ValueError):
#         return float("inf")


# def normalize_position(pos, ourlads_position=None, team=None):
#     """
#     Normalize a player's position for consistent bucketing.

#     Special case:
#       - If team is Seattle Seahawks or Baltimore Ravens AND Ourlads shows SLB, treat as DE.
#     """
#     pos_u = (pos or "").upper()
#     olads_u = (ourlads_position or "").upper()
#     team_u = (team or "").upper()

#     # Seahawks/Ravens: treat SLB as EDGE -> DE
#     if team_u in {"SEATTLE SEAHAWKS", "BALTIMORE RAVENS"} and "SLB" in olads_u:
#         return "DE"

#     # Standard LB-to-edge normalization if Ourlads signals OLB/RUSH
#     if olads_u and ("OLB" in olads_u or "RUSH" in olads_u):
#         return "DE"

#     position_map = {
#         "OLB": "LB",
#         "ILB": "LB",
#         "LB": "LB",
#     }

#     # Offensive line split hint using Ourlads anchor
#     if "/" in pos_u and olads_u:
#         if "C" in olads_u:
#             return "OC"
#         elif "G" in olads_u:
#             return "OG"
#         elif "T" in olads_u:
#             return "OT"

#     # Fallback: collapse LB variants or return original string
#     return position_map.get(pos_u, pos)


# def calculate_weighted_depth_avg(players):
#     weights = {"1": 1, "2": 2, "3": 3, "4": 4}
#     total_weight = 0
#     count = 0
#     for p in players:
#         weight = weights.get(str(p.get("depth_chart_position")), 5)
#         total_weight += weight
#         count += 1
#     return total_weight / count if count > 0 else float("inf")


# # --- Helpers for readable ranking logic ---------------------------------
# def _to_int(val):
#     try:
#         return int(val)
#     except (TypeError, ValueError):
#         return None


# def compute_rank_metrics(players):
#     """
#     Returns the counts used for sorting + depth_avg:
#       - depth_1_total: # starters (depth_chart_position == 1)
#       - first_round_total: # first-rounders (draft_round == 1)
#       - depth_2_total: # backups (depth_chart_position == 2)
#       - depth_avg: weighted average depth (lower is better)
#       - total_players: total players with depth_chart_position in {1,2,3}
#     """
#     depth_1_total = 0
#     depth_2_total = 0
#     first_round_total = 0
#     eligible_total = 0  # only depth_chart_position in {1,2,3}

#     for p in players:
#         dcp = str(p.get("depth_chart_position"))
#         if dcp == "1":
#             depth_1_total += 1
#             eligible_total += 1
#         elif dcp == "2":
#             depth_2_total += 1
#             eligible_total += 1
#         elif dcp == "3":
#             eligible_total += 1

#         if _to_int(p.get("draft_round")) == 1:
#             first_round_total += 1

#     return {
#         "depth_1_total": depth_1_total,
#         "first_round_total": first_round_total,
#         "depth_2_total": depth_2_total,
#         "depth_avg": calculate_weighted_depth_avg(players),
#         "total_players": eligible_total,  # used as "total_players_by_position" in the response
#     }


# BACKUPS_EQUIVALENCE_BAND = 2  # "±2 backups" equivalence window

# # def one_fewer_starter_override(candidate: Dict[str, int], opponent: Dict[str, int]) -> bool:
# #     """
# #     True if 'candidate' (which has exactly 1 fewer starter than 'opponent')
# #     should still rank higher.

# #     Rules:
# #       A) candidate has >=1 more backup AND >=1 more first-rounder AND >=2 more total players {1,2,3}
# #       B) candidate has >=2 more backups AND >= same first-rounders AND >=2 more total players {1,2,3}
# #     """
# #     cond_a = (
# #         (candidate["depth_2_total"]   >= opponent["depth_2_total"]   + 1) and
# #         (candidate["first_round_total"] >= opponent["first_round_total"] + 1) and
# #         (candidate["total_players"]   >= opponent["total_players"]   + 2)
# #     )
# #     cond_b = (
# #         (candidate["depth_2_total"]   >= opponent["depth_2_total"]   + 2) and
# #         (candidate["first_round_total"] >= opponent["first_round_total"]) and
# #         (candidate["total_players"]   >= opponent["total_players"]   + 2)
# #     )
# #     return cond_a or cond_b

# def one_fewer_starter_override(candidate: dict, opponent: dict) -> bool:
#     """
#     True if 'candidate' (which has exactly 1 fewer starter than 'opponent')
#     should still rank higher.

#     Rules:
#       A) +≥1 backup AND +≥1 first-rounder AND +≥2 total players {1,2,3}
#       B) +≥2 backups AND ≥ same first-rounders AND +≥2 total players {1,2,3}
#       C) +≥2 backups AND +≥1 first-rounder AND +≥1 total player {1,2,3}   <-- NEW
#     """
#     cond_a = (
#         candidate["depth_2_total"]     >= opponent["depth_2_total"]     + 1 and
#         candidate["first_round_total"] >= opponent["first_round_total"] + 1 and
#         candidate["total_players"]     >= opponent["total_players"]     + 2
#     )
#     cond_b = (
#         candidate["depth_2_total"]     >= opponent["depth_2_total"]     + 2 and
#         candidate["first_round_total"] >= opponent["first_round_total"]     and
#         candidate["total_players"]     >= opponent["total_players"]     + 2
#     )
#     # NEW: (+1 first-rounder, +2 backups, +1 total player)
#     cond_c = (
#         candidate["depth_2_total"]     >= opponent["depth_2_total"]     + 2 and
#         candidate["first_round_total"] >= opponent["first_round_total"] + 1 and
#         candidate["total_players"]     >= opponent["total_players"]     + 1
#     )
#     return cond_a or cond_b or cond_c


# SchoolRow = Tuple[str, Dict[str, Any]]

# def compare_schools(a: SchoolRow, b: SchoolRow) -> int:
#     """
#     Total ordering (keeps Texas A&M > LSU in your sample):

#       1) Most starters (depth_1_total), *with* the one-fewer-starter override.
#       2) If starters equal and backups differ by > ±2: most backups wins now.
#       3) If within the ±2 backups band: most first-rounders.
#       4) If still tied: most total players with depth in {1,2,3}.
#       5) If still tied: most backups.
#       6) If still tied: lowest avg depth (optional; off by default below).

#     Returns: -1 if a>b, 1 if b>a, 0 if equal under all tiebreaks.
#     """
#     (school_a, m_a), (school_b, m_b) = a, b

#     # 1) Starters (with one-fewer-starter override)
#     starters_a, starters_b = m_a["depth_1_total"], m_b["depth_1_total"]
#     if starters_a != starters_b:
#         # If A has exactly 1 fewer starter, can A overtake?
#         if starters_b == starters_a + 1 and one_fewer_starter_override(m_a, m_b):
#             return -1
#         # If B has exactly 1 fewer starter, can B overtake?
#         if starters_a == starters_b + 1 and one_fewer_starter_override(m_b, m_a):
#             return 1
#         # Otherwise, more starters wins
#         return -1 if starters_a > starters_b else 1

#     # 2) Large backups gap (> band) decides immediately
#     backups_a, backups_b = m_a["depth_2_total"], m_b["depth_2_total"]
#     if abs(backups_a - backups_b) > BACKUPS_EQUIVALENCE_BAND:
#         return -1 if backups_a > backups_b else 1

#     # 3) First-rounders (within the band)
#     fr_a, fr_b = m_a["first_round_total"], m_b["first_round_total"]
#     if fr_a != fr_b:
#         return -1 if fr_a > fr_b else 1

#     # 4) Total players in {1,2,3}
#     tot_a, tot_b = m_a["total_players"], m_b["total_players"]
#     if tot_a != tot_b:
#         return -1 if tot_a > tot_b else 1

#     # 5) Backups again (true tie-break)
#     if backups_a != backups_b:
#         return -1 if backups_a > backups_b else 1

#     # 6) Optional: lowest avg depth wins (uncomment if desired)
#     # avg_a, avg_b = m_a["depth_avg"], m_b["depth_avg"]
#     # if avg_a != avg_b:
#     #     return -1 if avg_a < avg_b else 1

#     return 0

# # -----------------------------------------------------------------------------


# class ThugPositionsBySchoolViewset(viewsets.ModelViewSet):

#     def list(self, request, *args, **kwargs):
#         all_teams = list(TEAM_IDS.keys())
#         players = ActiveNFLPlayers.objects.select_related("school").all()
#         filtered_players = [p for p in players if p.school and p.school.external_name in all_teams]

#         conference_summary = {}
#         national_position_ranks = {}
#         school_position_depth_players = defaultdict(lambda: defaultdict(list))

#         for player in filtered_players:
#             school = player.school
#             school_name = school.external_name
#             conference = school.conference or "Independent"
#             position = normalize_position(player.position, player.ourlads_position, team=player.team)

#             if conference not in conference_summary:
#                 conference_summary[conference] = {
#                     "total_players": 0,
#                     "players_by_position": defaultdict(lambda: {"total": 0}),
#                     "schools": {}
#                 }

#             conf_data = conference_summary[conference]

#             if school_name not in conf_data["schools"]:
#                 conf_data["schools"][school_name] = {
#                     "total_players": 0,
#                     "players_by_position": defaultdict(lambda: {"total": 0})
#                 }

#             school_data = conf_data["schools"][school_name]

#             round_val = player.draft_round
#             if not round_val or str(round_val).lower() in ["", "none", "null", "undrafted"]:
#                 round_label = "round_undrafted"
#             else:
#                 try:
#                     round_label = f"round_{int(round_val)}"
#                 except (ValueError, TypeError):
#                     round_label = "round_undrafted"

#             player_data = {
#                 "first_name": player.first_name,
#                 "last_name": player.last_name,
#                 "school": school_name,
#                 "nfl_team": player.team,
#                 "position": player.position,
#                 "ourlads_position": player.ourlads_position,
#                 "depth_chart_position": player.depth_chart_position,
#                 "draft_year": player.draft_year,
#                 "draft_round": player.draft_round,
#                 "overall_draft_pick": player.overall_draft_pick,
#             }

#             conf_data["total_players"] += 1
#             conf_pos = conf_data["players_by_position"][position]
#             conf_pos["total"] += 1
#             conf_pos.setdefault(round_label, {"total": 0, "players": []})
#             conf_pos[round_label]["total"] += 1
#             conf_pos[round_label]["players"].append(player_data)

#             school_data["total_players"] += 1
#             school_pos = school_data["players_by_position"][position]
#             school_pos["total"] += 1
#             school_pos.setdefault(round_label, {"total": 0, "players": []})
#             school_pos[round_label]["total"] += 1
#             school_pos[round_label]["players"].append(player_data)

#             # Track all players for national ranking (only if depth chart pos exists)
#             if player.depth_chart_position:
#                 school_position_depth_players[position][school_name].append(player_data)

#         # Rank by position totals at conference and school level
#         for position in set(pos for c in conference_summary.values() for pos in c["players_by_position"]):
#             totals = [(conf, data["players_by_position"].get(position, {}).get("total", 0))
#                       for conf, data in conference_summary.items()]
#             sorted_conf = sorted(totals, key=lambda x: x[1], reverse=True)
#             for i, (conf, _) in enumerate(sorted_conf, 1):
#                 if position in conference_summary[conf]["players_by_position"]:
#                     conference_summary[conf]["players_by_position"][position]["conference_rank"] = str(i)

#             for conf, conf_data in conference_summary.items():
#                 school_totals = [(school, data["players_by_position"].get(position, {}).get("total", 0))
#                                  for school, data in conf_data["schools"].items()]
#                 sorted_schools = sorted([s for s in school_totals if s[1] > 0], key=lambda x: x[1], reverse=True)
#                 for i, (school, _) in enumerate(sorted_schools, 1):
#                     if position in conf_data["schools"][school]["players_by_position"]:
#                         conf_data["schools"][school]["players_by_position"][position]["conference_school_rank"] = str(i)

#         # --- national_position_ranks with updated ordering (1st-rounders before total players) ---
#         for position, schools in school_position_depth_players.items():
#             rows = []
#             for school, players in schools.items():
#                 metrics = compute_rank_metrics(players)
#                 rows.append((school, metrics))

#             rows.sort(key=cmp_to_key(compare_schools))

#             national_position_ranks[position] = [
#                 {
#                     "school": school,
#                     "rank": i,
#                     "starters": m["depth_1_total"],
#                     "first_rounders": m["first_round_total"],
#                     "avg_depth_chart_position": round(m["depth_avg"], 3),
#                     "total_backups": m["depth_2_total"],
#                     "total_players_by_position": m["total_players"],  # only depth {1,2,3}
#                 }
#                 for i, (school, m) in enumerate(rows, 1)
#             ]
#             return Response(national_position_ranks)
#         # ----------------------------------------------------------------------

#         for conf_data in conference_summary.values():
#             for pos_data in conf_data["players_by_position"].values():
#                 for round_key in list(pos_data.keys()):
#                     if round_key.startswith("round_"):
#                         pos_data[round_key]["players"].sort(key=lambda p: parse_draft_pick(p["overall_draft_pick"]))
#                 rounds_sorted = sort_rounds({k: v for k, v in pos_data.items() if k.startswith("round_")})
#                 total_val = pos_data["total"]
#                 rank_val = pos_data.get("conference_rank")
#                 pos_data.clear()
#                 pos_data["total"] = total_val
#                 if rank_val:
#                     pos_data["conference_rank"] = rank_val
#                 pos_data.update(rounds_sorted)

#             conf_data["players_by_position"] = dict(
#                 sorted(conf_data["players_by_position"].items(), key=lambda x: x[1]["total"], reverse=True)
#             )

#             for school_data in conf_data["schools"].values():
#                 for pos_data in school_data["players_by_position"].values():
#                     for round_key in list(pos_data.keys()):
#                         if round_key.startswith("round_"):
#                             pos_data[round_key]["players"].sort(key=lambda p: parse_draft_pick(p["overall_draft_pick"]))
#                     rounds_sorted = sort_rounds({k: v for k, v in pos_data.items() if k.startswith("round_")})
#                     total_val = pos_data["total"]
#                     rank_val = pos_data.get("conference_school_rank")
#                     pos_data.clear()
#                     pos_data["total"] = total_val
#                     if rank_val:
#                         pos_data["conference_school_rank"] = rank_val
#                     pos_data.update(rounds_sorted)

#                 school_data["players_by_position"] = dict(
#                     sorted(school_data["players_by_position"].items(), key=lambda x: x[1]["total"], reverse=True)
#                 )

#         sorted_conferences = dict(
#             sorted(conference_summary.items(), key=lambda item: item[1]["total_players"], reverse=True)
#         )

#         return Response({
#             "conference_summary": sorted_conferences,
#             "national_position_ranks": national_position_ranks
#         })


# """
# THUG Position Algorithm (By Position)

# Ordering for national_position_ranks:
# 1. Most starters (depth_chart_position == 1)
#    1a. One-less-starter override (can jump ahead if depth/draft criteria are met)
# 2. If backups differ by > ±2: most backups wins now
# 3. If still within ±2: most first-rounders (draft_round == 1)
# 4. If still tied: most total players with depth_chart_position in {1, 2, 3}
# 5. If still tied: most backups (depth_chart_position == 2)
# 6. If still tied: lowest avg_depth_chart_position
# """


from collections import defaultdict, OrderedDict
from functools import cmp_to_key
from typing import Dict, Tuple, List, Any

from rest_framework import viewsets
from rest_framework.response import Response
from core.models.active_nfl_players import ActiveNFLPlayers

from webscraper.constants.ourlads_constants import TEAM_IDS


def sort_rounds(rounds_dict):
    desired_order = [f"round_{i}" for i in range(1, 8)] + ["round_undrafted"]
    return OrderedDict((key, rounds_dict[key]) for key in desired_order if key in rounds_dict)


def parse_draft_pick(pick):
    if isinstance(pick, str) and pick.lower() == "undrafted":
        return float("inf")
    try:
        return int(pick)
    except (TypeError, ValueError):
        return float("inf")


def normalize_position(pos, ourlads_position=None, team=None):
    """
    Normalize a player's position for consistent bucketing.

    Special case:
      - If team is Seattle Seahawks or Baltimore Ravens AND Ourlads shows SLB, treat as DE.
    """
    pos_u = (pos or "").upper()
    olads_u = (ourlads_position or "").upper()
    team_u = (team or "").upper()

    # Seahawks/Ravens: treat SLB as EDGE -> DE
    if team_u in {"SEATTLE SEAHAWKS", "BALTIMORE RAVENS"} and "SLB" in olads_u:
        return "DE"

    # Standard LB-to-edge normalization if Ourlads signals OLB/RUSH
    if olads_u and ("OLB" in olads_u or "RUSH" in olads_u):
        return "DE"

    position_map = {
        "OLB": "LB",
        "ILB": "LB",
        "LB": "LB",
    }

    # Offensive line split hint using Ourlads anchor
    if "/" in pos_u and olads_u:
        if "C" in olads_u:
            return "OC"
        elif "G" in olads_u:
            return "OG"
        elif "T" in olads_u:
            return "OT"

    # Fallback: collapse LB variants or return original string
    return position_map.get(pos_u, pos)


def calculate_weighted_depth_avg(players):
    weights = {"1": 1, "2": 2, "3": 3, "4": 4}
    total_weight = 0
    count = 0
    for p in players:
        weight = weights.get(str(p.get("depth_chart_position")), 5)
        total_weight += weight
        count += 1
    return total_weight / count if count > 0 else float("inf")


# --- Helpers for readable ranking logic ---------------------------------
def _to_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def compute_rank_metrics(players):
    """
    Returns the counts used for sorting + depth_avg:
      - depth_1_total: # starters (depth_chart_position == 1)
      - first_round_total: # first-rounders (draft_round == 1)
      - depth_2_total: # backups (depth_chart_position == 2)
      - depth_avg: weighted average depth (lower is better)
      - total_players: total players with depth_chart_position in {1,2,3}
    """
    depth_1_total = 0
    depth_2_total = 0
    first_round_total = 0
    eligible_total = 0  # only depth_chart_position in {1,2,3}

    for p in players:
        dcp = str(p.get("depth_chart_position"))
        if dcp == "1":
            depth_1_total += 1
            eligible_total += 1
        elif dcp == "2":
            depth_2_total += 1
            eligible_total += 1
        elif dcp == "3":
            eligible_total += 1

        if _to_int(p.get("draft_round")) == 1:
            first_round_total += 1

    return {
        "depth_1_total": depth_1_total,
        "first_round_total": first_round_total,
        "depth_2_total": depth_2_total,
        "depth_avg": calculate_weighted_depth_avg(players),
        "total_players": eligible_total,  # used as "total_players_by_position" in the response
    }


BACKUPS_EQUIVALENCE_BAND = 2  # "±2 backups" equivalence window


def one_fewer_starter_override(candidate: dict, opponent: dict) -> bool:
    """
    True if 'candidate' (which has exactly 1 fewer starter than 'opponent')
    should still rank higher.

    Rules:
      A) +≥1 backup AND +≥1 first-rounder AND +≥2 total players {1,2,3}
      B) +≥2 backups AND ≥ same first-rounders AND +≥2 total players {1,2,3}
      C) +≥2 backups AND +≥1 first-rounder AND +≥1 total player {1,2,3}   <-- NEW
    """
    cond_a = (
        candidate["depth_2_total"]     >= opponent["depth_2_total"]     + 1 and
        candidate["first_round_total"] >= opponent["first_round_total"] + 1 and
        candidate["total_players"]     >= opponent["total_players"]     + 2
    )
    cond_b = (
        candidate["depth_2_total"]     >= opponent["depth_2_total"]     + 2 and
        candidate["first_round_total"] >= opponent["first_round_total"]     and
        candidate["total_players"]     >= opponent["total_players"]     + 2
    )
    # NEW: (+1 first-rounder, +2 backups, +1 total player)
    cond_c = (
        candidate["depth_2_total"]     >= opponent["depth_2_total"]     + 2 and
        candidate["first_round_total"] >= opponent["first_round_total"] + 1 and
        candidate["total_players"]     >= opponent["total_players"]     + 1
    )
    return cond_a or cond_b or cond_c


SchoolRow = Tuple[str, Dict[str, Any]]


def compare_schools(a: SchoolRow, b: SchoolRow) -> int:
    """
    Total ordering:

      1) Most starters (depth_1_total), *with* the one-fewer-starter override.
      2) If starters equal and backups differ by > ±2: most backups wins now.
      3) If within the ±2 backups band: most first-rounders.
      4) If still tied: most total players with depth in {1,2,3}.
      5) If still tied: most backups.
      6) (optional) lowest avg depth.

    Returns: -1 if a>b, 1 if b>a, 0 if equal under all tiebreaks.
    """
    (school_a, m_a), (school_b, m_b) = a, b

    # 1) Starters (with one-fewer-starter override)
    starters_a, starters_b = m_a["depth_1_total"], m_b["depth_1_total"]
    if starters_a != starters_b:
        # If A has exactly 1 fewer starter, can A overtake?
        if starters_b == starters_a + 1 and one_fewer_starter_override(m_a, m_b):
            return -1
        # If B has exactly 1 fewer starter, can B overtake?
        if starters_a == starters_b + 1 and one_fewer_starter_override(m_b, m_a):
            return 1
        # Otherwise, more starters wins
        return -1 if starters_a > starters_b else 1

    # 2) Large backups gap (> band) decides immediately
    backups_a, backups_b = m_a["depth_2_total"], m_b["depth_2_total"]
    if abs(backups_a - backups_b) > BACKUPS_EQUIVALENCE_BAND:
        return -1 if backups_a > backups_b else 1

    # 3) First-rounders (within the band)
    fr_a, fr_b = m_a["first_round_total"], m_b["first_round_total"]
    if fr_a != fr_b:
        return -1 if fr_a > fr_b else 1

    # 4) Total players in {1,2,3}
    tot_a, tot_b = m_a["total_players"], m_b["total_players"]
    if tot_a != tot_b:
        return -1 if tot_a > tot_b else 1

    # 5) Backups again (true tie-break)
    if backups_a != backups_b:
        return -1 if backups_a > backups_b else 1

    # 6) Optional: lowest avg depth wins (uncomment if desired)
    # avg_a, avg_b = m_a["depth_avg"], m_b["depth_avg"]
    # if avg_a != avg_b:
    #     return -1 if avg_a < avg_b else 1

    return 0


def enforce_one_fewer_override_leapfrogs(rows: List[SchoolRow]) -> List[SchoolRow]:
    """
    Post-sort correction pass to resolve non-transitive artifacts.

    For any pair (upper=i, lower=j with j>i), if the lower team has exactly 1 fewer starter
    and qualifies for one_fewer_starter_override(lower, upper), move the lower team directly
    ABOVE that specific upper team (leapfrog), even if other teams sit between them.

    This ensures cases like Oregon (1 starter, but +FR/+backups/+total) rank ahead of
    Buffalo (2 starters) as intended by the override.
    """
    changed = True
    while changed:
        changed = False
        j = 1
        while j < len(rows):
            moved = False
            for i in range(j):
                upper = rows[i]
                lower = rows[j]
                mu, ml = upper[1], lower[1]
                if ml["depth_1_total"] + 1 == mu["depth_1_total"] and one_fewer_starter_override(ml, mu):
                    # Move lower just above this upper
                    rows.insert(i, rows.pop(j))
                    changed = True
                    moved = True
                    break
            if not moved:
                j += 1
    return rows


# -----------------------------------------------------------------------------


class ThugPositionsBySchoolViewset(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        all_teams = list(TEAM_IDS.keys())
        players = ActiveNFLPlayers.objects.select_related("school").all()
        filtered_players = [p for p in players if p.school and p.school.external_name in all_teams]

        conference_summary = {}
        national_position_ranks = {}
        school_position_depth_players = defaultdict(lambda: defaultdict(list))

        for player in filtered_players:
            school = player.school
            school_name = school.external_name
            conference = school.conference or "Independent"
            position = normalize_position(player.position, player.ourlads_position, team=player.team)

            if conference not in conference_summary:
                conference_summary[conference] = {
                    "total_players": 0,
                    "players_by_position": defaultdict(lambda: {"total": 0}),
                    "schools": {}
                }

            conf_data = conference_summary[conference]

            if school_name not in conf_data["schools"]:
                conf_data["schools"][school_name] = {
                    "total_players": 0,
                    "players_by_position": defaultdict(lambda: {"total": 0})
                }

            school_data = conf_data["schools"][school_name]

            round_val = player.draft_round
            if not round_val or str(round_val).lower() in ["", "none", "null", "undrafted"]:
                round_label = "round_undrafted"
            else:
                try:
                    round_label = f"round_{int(round_val)}"
                except (ValueError, TypeError):
                    round_label = "round_undrafted"

            player_data = {
                "first_name": player.first_name,
                "last_name": player.last_name,
                "school": school_name,
                "nfl_team": player.team,
                "position": player.position,
                "ourlads_position": player.ourlads_position,
                "depth_chart_position": player.depth_chart_position,
                "draft_year": player.draft_year,
                "draft_round": player.draft_round,
                "overall_draft_pick": player.overall_draft_pick,
            }

            conf_data["total_players"] += 1
            conf_pos = conf_data["players_by_position"][position]
            conf_pos["total"] += 1
            conf_pos.setdefault(round_label, {"total": 0, "players": []})
            conf_pos[round_label]["total"] += 1
            conf_pos[round_label]["players"].append(player_data)

            school_data["total_players"] += 1
            school_pos = school_data["players_by_position"][position]
            school_pos["total"] += 1
            school_pos.setdefault(round_label, {"total": 0, "players": []})
            school_pos[round_label]["total"] += 1
            school_pos[round_label]["players"].append(player_data)

            # Track all players for national ranking (only if depth chart pos exists)
            if player.depth_chart_position:
                school_position_depth_players[position][school_name].append(player_data)

        # Rank by position totals at conference and school level
        for position in set(pos for c in conference_summary.values() for pos in c["players_by_position"]):
            totals = [(conf, data["players_by_position"].get(position, {}).get("total", 0))
                      for conf, data in conference_summary.items()]
            sorted_conf = sorted(totals, key=lambda x: x[1], reverse=True)
            for i, (conf, _) in enumerate(sorted_conf, 1):
                if position in conference_summary[conf]["players_by_position"]:
                    conference_summary[conf]["players_by_position"][position]["conference_rank"] = str(i)

            for conf, conf_data in conference_summary.items():
                school_totals = [(school, data["players_by_position"].get(position, {}).get("total", 0))
                                 for school, data in conf_data["schools"].items()]
                sorted_schools = sorted([s for s in school_totals if s[1] > 0], key=lambda x: x[1], reverse=True)
                for i, (school, _) in enumerate(sorted_schools, 1):
                    if position in conf_data["schools"][school]["players_by_position"]:
                        conf_data["schools"][school]["players_by_position"][position]["conference_school_rank"] = str(i)

        # --- national_position_ranks with updated ordering and override leapfrogs ---
        for position, schools in school_position_depth_players.items():
            rows: List[SchoolRow] = []
            for school, players in schools.items():
                metrics = compute_rank_metrics(players)
                rows.append((school, metrics))

            # Primary comparator (pairwise)
            rows.sort(key=cmp_to_key(compare_schools))
            # Post-sort correction: leapfrog any target the override says they beat
            rows = enforce_one_fewer_override_leapfrogs(rows)

            national_position_ranks[position] = [
                {
                    "school": school,
                    "rank": i,
                    "starters": m["depth_1_total"],
                    "first_rounders": m["first_round_total"],
                    "avg_depth_chart_position": round(m["depth_avg"], 3),
                    "total_backups": m["depth_2_total"],
                    "total_players_by_position": m["total_players"],  # only depth {1,2,3}
                }
                for i, (school, m) in enumerate(rows, 1)
            ]
        # ----------------------------------------------------------------------

        for conf_data in conference_summary.values():
            for pos_data in conf_data["players_by_position"].values():
                for round_key in list(pos_data.keys()):
                    if round_key.startswith("round_"):
                        pos_data[round_key]["players"].sort(key=lambda p: parse_draft_pick(p["overall_draft_pick"]))
                rounds_sorted = sort_rounds({k: v for k, v in pos_data.items() if k.startswith("round_")})
                total_val = pos_data["total"]
                rank_val = pos_data.get("conference_rank")
                pos_data.clear()
                pos_data["total"] = total_val
                if rank_val:
                    pos_data["conference_rank"] = rank_val
                pos_data.update(rounds_sorted)

            conf_data["players_by_position"] = dict(
                sorted(conf_data["players_by_position"].items(), key=lambda x: x[1]["total"], reverse=True)
            )

            for school_data in conf_data["schools"].values():
                for pos_data in school_data["players_by_position"].values():
                    for round_key in list(pos_data.keys()):
                        if round_key.startswith("round_"):
                            pos_data[round_key]["players"].sort(key=lambda p: parse_draft_pick(p["overall_draft_pick"]))
                    rounds_sorted = sort_rounds({k: v for k, v in pos_data.items() if k.startswith("round_")})
                    total_val = pos_data["total"]
                    rank_val = pos_data.get("conference_school_rank")
                    pos_data.clear()
                    pos_data["total"] = total_val
                    if rank_val:
                        pos_data["conference_school_rank"] = rank_val
                    pos_data.update(rounds_sorted)

                school_data["players_by_position"] = dict(
                    sorted(school_data["players_by_position"].items(), key=lambda x: x[1]["total"], reverse=True)
                )

        sorted_conferences = dict(
            sorted(conference_summary.items(), key=lambda item: item[1]["total_players"], reverse=True)
        )

        return Response({
            "conference_summary": sorted_conferences,
            "national_position_ranks": national_position_ranks
        })


"""
THUG Position Algorithm (By Position)

Ordering for national_position_ranks:
1. Most starters (depth_chart_position == 1)
   1a. One-less-starter override (can jump ahead if depth/draft criteria are met)
2. If backups differ by > ±2: most backups wins now
3. If still within ±2: most first-rounders (draft_round == 1)
4. If still tied: most total players with depth_chart_position in {1, 2, 3}
5. If still tied: most backups (depth_chart_position == 2)
6. If still tied: lowest avg_depth_chart_position

Implementation notes:
- Added override Rule C (+1 FR, +2 backups, +1 total).
- Added enforce_one_fewer_override_leapfrogs(): after the global sort, leapfrog any team the override says they beat,
  even if they are not adjacent. This resolves cases like Oregon vs Buffalo being separated by intermediate teams.
"""
