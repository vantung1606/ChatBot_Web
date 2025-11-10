import json
from django.core.management.base import BaseCommand
from intent_manager.models import Intent, Pattern, Response
from Bot import path as bot_path

class Command(BaseCommand):
    help = 'Imports intents from content.json into the database'

    def handle(self, *args, **kwargs):
        # Xóa toàn bộ dữ liệu cũ để tránh trùng lặp
        self.stdout.write('Deleting old intent data...')
        Intent.objects.all().delete()

        json_path = bot_path.getJsonPath()
        self.stdout.write(f'Reading intents from {json_path}...')

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        intents_data = data.get('intents', [])
        count = 0
        for intent_data in intents_data:
            tag = intent_data['tag']
            product_url = intent_data.get('product_page_url')

            # Tạo Intent
            intent_obj, created = Intent.objects.get_or_create(
                tag=tag,
                defaults={'product_page_url': product_url}
            )

            # Tạo các Patterns
            for pattern_text in intent_data.get('patterns', []):
                Pattern.objects.create(intent=intent_obj, text=pattern_text)

            # Tạo các Responses
            for response_text in intent_data.get('responses', []):
                Response.objects.create(intent=intent_obj, text=response_text)

            count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} intents.'))
