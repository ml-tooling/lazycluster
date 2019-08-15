from typing import List, Union


def get_remaining_ports(ports: List[int], last_used_port: int) -> List[int]:
    """Get a new list with the remaining ports after cutting out all ports until and incl. the last used port.

    Args:
        ports (List[int]): The port list to be updated.
        last_used_port (int): The last port that was actually used. All ports up this one and including this one will
                              be removed.
    Returns:
        List with remaining ports
    """
    skip = True
    final_port_list = []
    for port in ports:
        if skip:
            if port == last_used_port:
                skip = False
            continue
        final_port_list.append(port)
    return final_port_list


def create_list_from_parameter_value(value: Union[object, List[object], None]) -> list:
    """Many methods can either take a single value, a list or None as input. Usually we want to iterate all given
    values. Therefore, this method ensures that a list is always returned.

    Args:
        value (Union[object, List[object], None])): The value that will be mapped onto a list representation.

    Returns:
        List[object]: Either an empty list or a list with all given objects.

    Examples:
        value = None    => []
        value = []      => []
        value = 5       => [5]
        value = [5,6]   => [5,6]
    """
    if not value:
        # => create empty list
        return []
    if not isinstance(value, list):
        # => create list with single value
        return [value]
    # => value is already a list
    return value
