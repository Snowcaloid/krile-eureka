#
# This file is part of Orbyt. (https://github.com/nxmrqlly/orbyt)
# Copyright (c) 2023-present Ritam Das
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
For formatting stuff
"""

def truncate(string: str, width: int = 50) -> str:
    """
    Truncates the given `text` to the given `width`.

    Parameters
    -----------
    text: :class:`str`
        The text to truncate.
    width: :class:`int`
        The width of the text.

    Returns
    --------
    :class:`str`
        The truncated text.
    """

    if len(string) > width:
        string = string[: width - 3] + "..."
    return string
