"""
distrochooser
Copyright (C) 2014-2025  Christoph Müller  <mail@chmr.eu>

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

from web.models import LanguageFeedback
from django.core.management.base import BaseCommand
from logging import getLogger, ERROR

logger = getLogger('command')

class Command(BaseCommand):
    help = "Review provided language feedback"
    def add_arguments(self, parser):
        parser.add_argument("lang_code", type=str)
        parser.add_argument("--delete", type=int, nargs="*")
        parser.add_argument("--approve", type=int, nargs="*")
        parser.add_argument("--clear", type=bool, nargs="?")
    def handle(self, *args, **options):
        lang_code = options["lang_code"]
        to_delete = options["delete"]
        to_approve = options["approve"]
        remove_unapproved = options["clear"]
        if to_delete is not None:
            for pk in to_delete:
                LanguageFeedback.objects.filter(pk=pk).delete()
        if to_approve is not None:
            for pk in to_approve:
                obj = LanguageFeedback.objects.filter(pk=pk).first()
                obj.is_approved = not obj.is_approved
                obj.save()
                LanguageFeedback.objects.filter(session__language_code=lang_code).filter(language_key=obj.language_key).exclude(pk=pk).delete()
        if remove_unapproved:
            LanguageFeedback.objects.filter(session__language_code=lang_code).exclude(is_approved=True).delete()
        data = LanguageFeedback.objects.filter(session__language_code=lang_code)
        for element in data:
            print(f"[{'X' if element.is_approved else ' '}] {element.pk} {element.language_key} => {element.value}")
            # TODO: Store accepted translations in files
