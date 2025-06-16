def compute_diff(old: str, new: str):
    """
    Tente de détecter un seul caractère inséré ou supprimé entre old et new.
    Si c'est trop complexe, retourne une opération 'skip'.
    """
    if old == new:
        return {'action': 'skip'}

    # repère le premier index où les deux chaînes diffèrent
    for idx, (co, cn) in enumerate(zip(old, new)):
        if co != cn:
            break
    else:
        idx = min(len(old), len(new))

    delta = len(new) - len(old)

    if delta >0:
        # insertion simple
        return {'action': 'insert'}
    elif delta < 0:
        # suppression simple
        return {'action': 'delete'}
    else:
        # modification trop complexe (remplacement, plusieurs insertions...)
        return {'action': 'skip'}
