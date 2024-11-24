from django.core.management.base import BaseCommand
from django.utils.text import slugify
from contentblock.models import ContentBlock
from contentblock.utils import refresh_contentblock_paths
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Fix content block image paths and verify file existence'

    def handle(self, *args, **options):
        content_blocks = ContentBlock.objects.all()
        fixed_count = 0
        missing_count = 0
        
        self.stdout.write('Starting content block path verification...')
        
        for block in content_blocks:
            if block.image:
                # Get expected path
                page_slug = slugify(block.page.title)
                expected_path = f'pages/{page_slug}/images/{os.path.basename(block.image.name)}'
                actual_path = block.image.name
                
                # Check if file exists
                full_path = os.path.join(settings.MEDIA_ROOT, actual_path)
                file_exists = os.path.isfile(full_path)
                
                if not file_exists or expected_path != actual_path:
                    self.stdout.write(self.style.WARNING(
                        f'Issue found with ContentBlock {block.id}:\n'
                        f'Title: {block.title}\n'
                        f'Current path: {actual_path}\n'
                        f'Expected path: {expected_path}\n'
                        f'File exists: {file_exists}'
                    ))
                    
                    if file_exists:
                        # Fix path if file exists but path is wrong
                        refresh_contentblock_paths(block, page_slug)
                        fixed_count += 1
                    else:
                        missing_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\nVerification complete:\n'
            f'- Fixed paths: {fixed_count}\n'
            f'- Missing files: {missing_count}\n'
            f'- Total checked: {content_blocks.count()}'
        )) 