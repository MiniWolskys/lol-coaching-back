def print_result(res: list) -> None:
    """
    Simple function to print the result in terminal.

    :param res: list of all elements to be printed.
    :return: None
    """
    for elem in res:
        print(f"On {elem['count']} games as {elem['filter']}:")
        for stat in elem['stats']:
            print(f"\t{stat['statName']} : {stat['statValue']:.2f}{'%' if stat['statType'] == '%' else ''}")
        if elem['winCount'] > 0:
            print(f"On {elem['winCount']} wins:")
            for stat in elem['winStats']:
                print(f"\t{stat['statName']} : {stat['statValue']:.2f}{'%' if stat['statType'] == '%' else ''}")
        else:
            print(f"No win for {elem['filter']}")
        if elem['lossCount'] > 0:
            print(f"On {elem['lossCount']} losses:")
            for stat in elem['lossStats']:
                print(f"\t{stat['statName']} : {stat['statValue']:.2f}{'%' if stat['statType'] == '%' else ''}")
        else:
            print(f"No loss for {elem['filter']}")
        print("----------------------------------------------")


def format_to_print(elem: dict, count: int, selected: str) -> dict:
    """
    Function to format a element before printing it.

    :param elem: dictionary containing all information we wish to add to the object.
    :param count: An integer being the number of games played according to the filter.
    :param selected: String used for filter, such as role or champion.
    :return: A dictionary ready to be printed or used by other functions.
    """
    new_elem = {
        'count': count,
        'filter': selected,
        'stats': [],
        'winStats': [],
        'lossStats': [],
        'winCount': 0,
        'lossCount': 0
    }

    for stat in elem:
        if "win" in stat:
            if stat == "wins":
                new_elem["winCount"] = elem[stat]
            else:
                new_elem['winStats'].append({'statName': stat.replace("win", ""), 'statValue': elem[stat],
                                             'statType': '%' if 'Share' in stat or 'Efficiency' in stat else 'int'})
        elif "loss" in stat:
            if stat == "losses":
                new_elem["lossCount"] = elem[stat]
            else:
                new_elem['lossStats'].append({'statName': stat.replace("loss", ""), 'statValue': elem[stat],
                                              'statType': '%' if 'Share' in stat or 'Efficiency' in stat else 'int'})
        else:
            new_elem['stats'].append({'statName': stat, 'statValue': elem[stat],
                                      'statType': '%' if 'Share' in stat or 'Efficiency' in stat else 'int'})

    return new_elem
