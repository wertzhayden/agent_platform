from collections import defaultdict, OrderedDict

from rest_framework import viewsets
from rest_framework.response import Response
from core.models.active_nfl_players import ActiveNFLPlayers
from core.serializers.active_nfl_player_serializer import ActiveNFLPlayerSerializer

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
    
def normalize_position(pos, ourlads_position=None):
    # Standard LB normalization
    position_map = {
        "OLB": "LB",
        "ILB": "LB",
        "LB": "LB",
    }

    if "/" in pos and ourlads_position:
        ourlads_position = ourlads_position.upper()
        if "C" in ourlads_position:
            return "OC"
        elif "G" in ourlads_position:
            return "OG"
        elif "T" in ourlads_position:
            return "OT"

    return position_map.get(pos.upper(), pos)

def calculate_weighted_depth_avg(players):
        weights = {"1": 1, "2": 2, "3": 3, "4": 4}
        total_weight = 0
        count = 0
        for p in players:
            weight = weights.get(str(p.get("depth_chart_position")), 5)
            total_weight += weight
            count += 1
        return total_weight / count if count > 0 else float("inf")

class ThugPositionsBySchoolViewset(viewsets.ModelViewSet):
    """
    Thug Position Algorithm
        1. Active NFL Players by school
        2. # of players by Position
            Example: RB Example: 5 active RB’s
        3. The Depth Chart rank by Position (e.g. 1st string, 2nd, 3rd, etc...)
            RB Example: 4 are starters & 1 is a 2nd stringer
        4. The Draft Choice by Position (e.g. 1st round through undrafted)
            RB Example: 3 1st rounders, 1 in 2nd & 1 in 3rd. Average pick # of 40
        5. The (Avg Years of Experience) by Position
            RB Example: Derrick Henry has 10 YOE, Jacobs has 6, Gibbs has 2, so average would be 6 YOE for RB
    """
    # def list(self, request, *args, **kwargs):

    #     all_teams = list(TEAM_IDS.keys())
    #     players = ActiveNFLPlayers.objects.select_related("school").all()
    #     filtered_players = [p for p in players if p.school and p.school.external_name in all_teams]

    #     conference_summary = {}
    #     national_position_ranks = defaultdict(list)
    #     school_position_totals = defaultdict(lambda: defaultdict(int))

    #     for player in filtered_players:
    #         school = player.school
    #         school_name = school.external_name
    #         conference = school.conference or "Independent"
    #         position = normalize_position(player.position, player.ourlads_position)

    #         if conference not in conference_summary:
    #             conference_summary[conference] = {
    #                 "total_players": 0,
    #                 "players_by_position": defaultdict(lambda: {"total": 0}),
    #                 "schools": {}
    #             }

    #         conf_data = conference_summary[conference]

    #         if school_name not in conf_data["schools"]:
    #             conf_data["schools"][school_name] = {
    #                 "total_players": 0,
    #                 "players_by_position": defaultdict(lambda: {"total": 0})
    #             }

    #         school_data = conf_data["schools"][school_name]

    #         round_val = player.draft_round
    #         if not round_val or str(round_val).lower() in ["", "none", "null", "undrafted"]:
    #             round_label = "round_undrafted"
    #         else:
    #             try:
    #                 round_label = f"round_{int(round_val)}"
    #             except (ValueError, TypeError):
    #                 round_label = "round_undrafted"

    #         player_data = {
    #             "first_name": player.first_name,
    #             "last_name": player.last_name,
    #             "school": school_name,
    #             "nfl_team": player.team,
    #             "position": player.position,
    #             "ourlads_position": player.ourlads_position,
    #             "depth_chart_position": player.depth_chart_position,
    #             "draft_year": player.draft_year,
    #             "draft_round": player.draft_round,
    #             "overall_draft_pick": player.overall_draft_pick,
    #         }

    #         # Update conference data
    #         conf_data["total_players"] += 1
    #         conf_pos = conf_data["players_by_position"][position]
    #         conf_pos["total"] += 1
    #         conf_pos.setdefault(round_label, {"total": 0, "players": []})
    #         conf_pos[round_label]["total"] += 1
    #         conf_pos[round_label]["players"].append(player_data)

    #         # Update school data
    #         school_data["total_players"] += 1
    #         school_pos = school_data["players_by_position"][position]
    #         school_pos["total"] += 1
    #         school_pos.setdefault(round_label, {"total": 0, "players": []})
    #         school_pos[round_label]["total"] += 1
    #         school_pos[round_label]["players"].append(player_data)

    #         # Track for national rank
    #         school_position_totals[position][school_name] += 1

    #     # Rank by position totals at conference and school level
    #     for position in set(pos for c in conference_summary.values() for pos in c["players_by_position"]):
    #         # Conference-wide position ranking
    #         totals = [(conf, data["players_by_position"].get(position, {}).get("total", 0))
    #                 for conf, data in conference_summary.items()]
    #         sorted_conf = sorted(totals, key=lambda x: x[1], reverse=True)
    #         for i, (conf, _) in enumerate(sorted_conf, 1):
    #             if position in conference_summary[conf]["players_by_position"]:
    #                 conference_summary[conf]["players_by_position"][position]["conference_rank"] = str(i)

    #         for conf, conf_data in conference_summary.items():
    #             school_totals = [(school, data["players_by_position"].get(position, {}).get("total", 0))
    #                             for school, data in conf_data["schools"].items()]
    #             sorted_schools = sorted([s for s in school_totals if s[1] > 0], key=lambda x: x[1], reverse=True)
    #             for i, (school, _) in enumerate(sorted_schools, 1):
    #                 if position in conf_data["schools"][school]["players_by_position"]:
    #                     conf_data["schools"][school]["players_by_position"][position]["conference_school_rank"] = str(i)

    #     # Build national_position_ranks
    #     for position, schools in school_position_totals.items():
    #         sorted_schools = sorted(schools.items(), key=lambda x: x[1], reverse=True)
    #         national_position_ranks[position] = [
    #             {"school": school, "total": total, "rank": i + 1}
    #             for i, (school, total) in enumerate(sorted_schools)
    #         ]

    #     # Sorting step
    #     for conf_data in conference_summary.values():
    #         for pos_data in conf_data["players_by_position"].values():
    #             for round_key in list(pos_data.keys()):
    #                 if round_key.startswith("round_"):
    #                     pos_data[round_key]["players"].sort(key=lambda p: parse_draft_pick(p["overall_draft_pick"]))
    #             rounds_sorted = sort_rounds({k: v for k, v in pos_data.items() if k.startswith("round_")})
    #             total_val = pos_data["total"]
    #             rank_val = pos_data.get("conference_rank")
    #             pos_data.clear()
    #             pos_data["total"] = total_val
    #             if rank_val:
    #                 pos_data["conference_rank"] = rank_val
    #             pos_data.update(rounds_sorted)

    #         conf_data["players_by_position"] = dict(
    #             sorted(conf_data["players_by_position"].items(), key=lambda x: x[1]["total"], reverse=True)
    #         )

    #         for school_data in conf_data["schools"].values():
    #             for pos_data in school_data["players_by_position"].values():
    #                 for round_key in list(pos_data.keys()):
    #                     if round_key.startswith("round_"):
    #                         pos_data[round_key]["players"].sort(key=lambda p: parse_draft_pick(p["overall_draft_pick"]))
    #                 rounds_sorted = sort_rounds({k: v for k, v in pos_data.items() if k.startswith("round_")})
    #                 total_val = pos_data["total"]
    #                 rank_val = pos_data.get("conference_school_rank")
    #                 pos_data.clear()
    #                 pos_data["total"] = total_val
    #                 if rank_val:
    #                     pos_data["conference_school_rank"] = rank_val
    #                 pos_data.update(rounds_sorted)

    #             school_data["players_by_position"] = dict(
    #                 sorted(school_data["players_by_position"].items(), key=lambda x: x[1]["total"], reverse=True)
    #             )

    #     sorted_conferences = dict(
    #         sorted(conference_summary.items(), key=lambda item: item[1]["total_players"], reverse=True)
    #     )

    #     return Response({
    #         "conference_summary": sorted_conferences,
    #         "national_position_ranks": national_position_ranks
    #     })

    def list(self, request, *args, **kwargs):
        all_teams = list(TEAM_IDS.keys())
        players = ActiveNFLPlayers.objects.select_related("school").all()
        filtered_players = [p for p in players if p.school and p.school.external_name in all_teams]

        conference_summary = {}
        national_position_ranks = defaultdict(list)
        school_position_depth_players = defaultdict(lambda: defaultdict(list))

        for player in filtered_players:
            school = player.school
            school_name = school.external_name
            conference = school.conference or "Independent"
            position = normalize_position(player.position, player.ourlads_position)

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

            # Track all players for ranking calculation
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

        # Build enhanced national_position_ranks
        for position, schools in school_position_depth_players.items():
            rank_buckets = defaultdict(list)
            for school, players in schools.items():
                depth_1_count = sum(1 for p in players if str(p.get("depth_chart_position")) == "1")
                rank_buckets[depth_1_count].append((school, calculate_weighted_depth_avg(players)))

            sorted_ranks = []
            for depth_1_count in sorted(rank_buckets.keys(), reverse=True):
                tied_schools = sorted(rank_buckets[depth_1_count], key=lambda x: x[1])
                sorted_ranks.extend(tied_schools)

            national_position_ranks[position] = [
                {"school": school, "depth_1_total": depth_1, "depth_avg": round(avg, 3), "rank": i + 1}
                for i, (school, avg) in enumerate(sorted_ranks)
                for depth_1 in [sum(1 for p in school_position_depth_players[position][school] if str(p.get("depth_chart_position")) == "1")]
            ]

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


1. Who has the most Active NFL Starters?

2. Who has the lowest average depth_chart_position?
    a. Starter = 1, Backup = 2, 3rd string = 3, 4th string = 4

3. Who has the lowest average draft_round?
    a. Example: 1st rounder = 1, 2nd rounder = 2, 3rd rounder = 3, etc...

4. What AFTER the Top 3?

    a. Who has the most Active NFL Players?
    b. who has the most backups?


THOUGHTS

1. Starter = 1, Backup = 2, 3rd string = 3, 4th string = 4
2. Draft Round = 1st = 1, 2nd = 2, 3rd = 3, 4th = 4, 5th = 5, 6th = 6, 7th = 7

Must be within (+/- 1) of the Total Active NFL Players by position ??

Example:

Acceptable Windows for Total Active NFL Players by Position:

12 - 8
7 - 5
4 - 3
2 - 0

1. Pull the NFL Depth Charts from Ourlads & pull the Defense that each team uses. (3-4) to determine EDGE vs OLB
2. Pull the NFL Position such as Nickle, 3-4 OLB, etc...
3. What is the Avg of Players by Position per Round in the NFL Draft (Use 10 year data)? 

Thug Position Algo - https://chatgpt.com/c/688cb54a-ba60-8324-9faf-8f3d22414ea4

"""