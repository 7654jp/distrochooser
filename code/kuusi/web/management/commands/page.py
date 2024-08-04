"""
kuusi
Copyright (C) 2014-2024  Christoph Müller  <mail@chmr.eu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from typing import Dict, List, Callable
from web.models import Page, SessionVersion
from logging import getLogger

logger = getLogger('command') 
def create_pages(get_or_default: Callable[[str, Dict], any], haystack: Dict) -> List[Page]:
        """
        Create the pages in two loops:
        1. Create the pages without next_page set
        2. Update the page with the next_page (if any)
        """
        got = []
        
        # Create the stub pages in the first loop
        for catalogue_id, properties in haystack.items():
            logger.info(f"Current: {catalogue_id}")
            new_page = Page(
                catalogue_id = catalogue_id,
                can_be_marked = get_or_default("can_be_marked", properties),
                require_session  = get_or_default("require_session", properties)
            )
            new_page.save()
            
        # Assign the next pages after all pages are created
        for catalogue_id, properties in haystack.items():
            page = Page.objects.get(catalogue_id=catalogue_id)
            # Only assign a next page if there is one
            next_catalogue_id = properties["next_page"] if "next_page" in properties else None
            if next_catalogue_id:
                logger.info(f"Trying to assign next page from {next_catalogue_id} to {page}")
                page.next_page =  Page.objects.get(catalogue_id=next_catalogue_id)
            not_in_versions = get_or_default("not_in_versions", properties)

            if len(not_in_versions) > 0:
                version_name: str
                for version_name in not_in_versions:
                    page.not_in_versions.add(SessionVersion.objects.get(version_name=version_name))

            page.save()
            got.append(page)

        return got

        