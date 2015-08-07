def player_list_to_win_loss_tuple(plist):
    """Given a list, returns a tuple of ([winners], [losers])"""
    if len(plist) <=1 or len(plist) > 4:
        raise ValueError("Must have at least 2 and no more than 4 players:{}"
                         .format(plist))
    plist = list(map(lambda p: p.strip().lower(), plist))
    if len(plist) == 2:
        return ([plist[0]], [plist[1]])
    elif len(plist) == 3:
        return ([plist[0]], plist[1:])
    return (plist[0:2], plist[2:])
