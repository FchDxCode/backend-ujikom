# The `DynamicDataService` class provides methods to retrieve popular photos, latest information,
# agendas, and albums with error handling for each operation.
from page.models import Page
from contentblock.models import ContentBlock
from photo.models import Photo
from album.models import Album
from django.utils.text import slugify
from django.db.models import Prefetch
from category.models import Category

class DynamicDataService:
    @staticmethod
    def get_popular_photos(language='id', limit=3):
        try:
            photos = Photo.objects.select_related(
                'album',
                'album__category'
            ).filter(
                album__in=Album.objects.filter(
                    is_active=True,
                    category__in=Category.objects.all()
                )
            ).order_by('-likes')[:limit]

            return [
                {
                    'id': photo.id,
                    'type': 'photo',
                    'title': photo.title,
                    'slug': f"{slugify(photo.title)}-{photo.id}",
                    'likes': photo.likes,
                    'category': {
                        'id': photo.album.category.id,
                        'name': photo.album.category.name,
                        'slug': photo.album.category.slug
                    },
                    'album': {
                        'id': photo.album.id,
                        'title': photo.album.title,
                        'slug': f"{slugify(photo.album.title)}-{photo.album.id}"
                    },
                    'text': f"{photo.title} ({photo.likes} {'suka' if language == 'id' else 'likes'})"
                }
                for idx, photo in enumerate(photos)
            ]
        except Exception as e:
            print(f"Error getting popular photos: {str(e)}")
            return []


    # @staticmethod
    # def get_latest_informasi(language='id', limit=3):
    #     try:
    #         content_blocks = ContentBlock.objects.filter(
    #             page__slug='informasi'
    #             # Removed 'page__is_active=True'
    #         ).select_related('page').order_by('-updated_at')[:limit]

    #         return [
    #             {
    #                 'id': block.id,
    #                 'type': 'informasi',
    #                 'title': block.title,
    #                 'text': f"{idx + 1}. {block.title}",
    #                 'slug': f"{slugify(block.title)}-{block.id}",
    #                 'date': block.updated_at.strftime('%d/%m/%Y')
    #             }
    #             for idx, block in enumerate(content_blocks)
    #         ]
    #     except Exception as e:
    #         print(f"Error getting latest informasi: {str(e)}")
    #         return []


    # @staticmethod
    # def get_latest_agenda(language='id', limit=3):
    #     try:
    #         content_blocks = ContentBlock.objects.filter(
    #             page__slug='agenda'
    #             # Removed 'page__is_active=True'
    #         ).select_related('page').order_by('-updated_at')[:limit]

    #         return [
    #             {
    #                 'id': block.id,
    #                 'type': 'agenda',
    #                 'title': block.title,
    #                 'text': f"{idx + 1}. {block.title}",
    #                 'slug': f"{slugify(block.title)}-{block.id}",
    #                 'date': block.updated_at.strftime('%d/%m/%Y')
    #             }
    #             for idx, block in enumerate(content_blocks)
    #         ]
    #     except Exception as e:
    #         print(f"Error getting latest agenda: {str(e)}")
    #         return []


    # @staticmethod
    # def get_latest_albums(language='id', limit=5):
    #     try:
    #         albums = Album.objects.filter(
    #             is_active=True,
    #             # Removed 'is_public=True' as it doesn't exist in Album model
    #             category__in=Category.objects.all()  # Removed 'is_active' filter
    #         ).select_related('category').prefetch_related(
    #             'photos'
    #         ).order_by('-created_at')[:limit]

    #         return [
    #             {
    #                 'id': album.id,
    #                 'type': 'album',
    #                 'title': album.title,
    #                 'slug': f"{slugify(album.title)}-{album.id}",
    #                 'category': {
    #                     'id': album.category.id,
    #                     'name': album.category.name,
    #                     'slug': album.category.slug
    #                 },
    #                 'text': f"{idx + 1}. {album.title} ({album.photos.count()} {'foto' if language == 'id' else 'photos'})"
    #             }
    #             for idx, album in enumerate(albums)
    #         ]
    #     except Exception as e:
    #         print(f"Error getting latest albums: {str(e)}")
    #         return []