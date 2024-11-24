import random

class GalleryResponses:
    """Kelas untuk mengelola semua respons dan pertanyaan yang tersedia"""

    # Daftar intent dan kata kunci terkait
    INTENTS = {
        'about': [
            'tentang', 'about', 'info', 'information', 'gallery ini', 'website ini',
            'apa ini', 'jelaskan', 'ceritakan', 'tell me about'
        ],
        'popular_photos': [
            'foto populer', 'popular photos', 'like terbanyak', 'most liked', 'terpopuler',
            'foto dengan like', 'photo with most likes', 'foto yang disukai', 
            'photo dengan like terbanyak', 'foto paling banyak like', 'foto favorit'
        ],
        'greeting': [
            'hai', 'hello', 'hi', 'halo', 'hei', 'selamat pagi', 'selamat siang',
            'selamat malam', 'good morning', 'good afternoon', 'good evening'
        ],
        'casual': [
            'apa kabar', 'how are you', 'lagi apa', 'what are you doing',
            'siapa kamu', 'who are you', 'kamu siapa'
        ]
    }

    # Daftar respons berdasarkan intent dan bahasa
    RESPONSES = {
        'about': {
            'id': {
                'text': '''
                Hai! Selamat datang di galeri foto kami! 📸✨
                
                Di sini, kamu bisa:
                • Menjelajahi berbagai kategori foto yang menarik
                • Menemukan foto-foto yang paling banyak disukai
                • Menikmati karya fotografi yang keren dan inspiratif
                
                Mau tahu foto apa yang lagi hits? Tanyakan aja ke aku! 😊
                ''',
                'embedding': None
            },
            'en': {
                'text': '''
                Hi there! Welcome to our photo gallery! 📸✨
                
                Here, you can:
                • Browse through various interesting photo categories
                • Discover the most liked photos
                • Enjoy stunning and inspiring photography works
                
                Want to know which photos are trending? Just ask me! 😊
                ''',
                'embedding': None
            }
        },
        'casual': {
            'id': {
                'text': [
                    "Aku baik-baik saja! Senang bisa bantu kamu menjelajahi galeri foto kita! 😊",
                    "Halo! Aku Cerbi, asisten virtual yang suka banget sama foto-foto keren! Mau lihat foto populer? 📸",
                    "Senang ngobrol sama kamu! Ada yang mau kamu tanyakan tentang galeri kita? 🌟"
                ]
            },
            'en': {
                'text': [
                    "I'm good! Happy to help you explore our photo gallery! 😊",
                    "Hello! I'm Cerbi, a virtual assistant who loves awesome photos! Want to see some popular ones? 📸",
                    "Nice chatting with you! Anything you want to ask about our gallery? 🌟"
                ]
            }
        }
    }

    # Daftar pertanyaan yang disarankan
    SUGGESTED_QUESTIONS = {
        'id': [
            "Bagaimana cara melihat foto?",
            "Apa saja kategori yang ada?",
            "Bagaimana mencari foto tertentu?",
            "Ceritakan lebih banyak tentang galeri ini.",
            "Apakah ada fitur pencarian?",
            "Bagaimana cara memfilter foto?",
            "Dimana saya bisa melihat album favorit?",
            "Apakah ada panduan penggunaan?"
        ],
        'en': [
            "How do I view photos?",
            "What categories are available?",
            "How can I search for specific photos?",
            "Tell me more about this gallery.",
            "Is there a search feature?",
            "How do I filter photos?",
            "Where can I see my favorite albums?",
            "Is there a user guide?"
        ]
    }

    # Respons umum dan error
    GENERAL_RESPONSES = {
        'error': {
            'id': "Ups, maaf ya! Aku agak bingung nih 😅 Coba tanya dengan cara lain?",
            'en': "Oops, my bad! I'm a bit confused 😅 Could you try asking differently?"
        },
        'not_understood': {
            'id': "Hmm... Aku kurang paham nih 🤔 Bisa jelasin lagi dengan cara lain?",
            'en': "Hmm... I didn't quite catch that 🤔 Could you explain it differently?"
        },
        'greeting': {
            'id': [
                "Hai! Cerbi di sini! Mau lihat-lihat foto keren? 🌟",
                "Halo! Aku Cerbi, siap bantu kamu jelajahi galeri foto kita! ✨",
                "Hai hai! Senang ketemu kamu! Mau tau foto apa yang lagi populer? 😊"
            ],
            'en': [
                "Hi there! Cerbi here! Want to see some cool photos? 🌟",
                "Hello! I'm Cerbi, ready to help you explore our gallery! ✨",
                "Hey! Nice to meet you! Want to know what photos are trending? 😊"
            ]
        }
    }

    # Definisi level emosi
    EMOTION_LEVELS = {
        'very_positive': ['5 stars'],
        'positive': ['4 stars'],
        'neutral': ['3 stars'],
        'negative': ['2 stars'],
        'very_negative': ['1 star']
    }

    # Ekspresi emosi berdasarkan konteks
    EMOTIONAL_EXPRESSIONS = {
        'very_positive': {
            'id': {
                'prefix': [
                    "Yeay! Senang banget bisa bantu! ",
                    "Asik! Aku tahu nih! ",
                    "Wah, ini bisa aku bantu! "
                ],
                'suffix': [
                    " 😊✨",
                    " Semoga membantu ya! 🌟",
                    " Semoga info ini berguna! 💫"
                ]
            },
            'en': {
                'prefix': [
                    "Yay! So happy to help! ",
                    "Awesome! I know this! ",
                    "Oh, I can help with that! "
                ],
                'suffix': [
                    " 😊✨",
                    " Hope this helps! 🌟",
                    " Hope this info is useful! 💫"
                ]
            }
        },
        'positive': {
            'id': {
                'prefix': [
                    "Tentu! ",
                    "Dengan senang hati, ",
                    "Aku bisa bantu itu! "
                ],
                'suffix': [
                    " 😊",
                    " Semoga membantu!",
                    " Ada yang lain yang bisa aku bantu?"
                ]
            },
            'en': {
                'prefix': [
                    "Of course! ",
                    "I'd be happy to help! ",
                    "I can definitely help with that! "
                ],
                'suffix': [
                    " 😊",
                    " Hope that helps!",
                    " Anything else I can assist you with?"
                ]
            }
        },
        'neutral': {
            'id': {
                'prefix': [
                    "Baik, ",
                    "Oke, ",
                    "Begini, "
                ],
                'suffix': [
                    ".",
                    " Ada lagi yang ingin ditanyakan?",
                    " Semoga informasinya membantu."
                ]
            },
            'en': {
                'prefix': [
                    "Alright, ",
                    "Okay, ",
                    "Here's what you need to know: "
                ],
                'suffix': [
                    ".",
                    " Any other questions?",
                    " Hope this information helps."
                ]
            }
        },
        'negative': {
            'id': {
                'prefix': [
                    "Maaf ya, ",
                    "Aku mengerti kebingunganmu. ",
                    "Mari aku coba jelaskan lagi, "
                ],
                'suffix': [
                    " Semoga ini membantu.",
                    " Apakah penjelasan ini cukup jelas?",
                    " Beri tahu aku jika masih ada yang membingungkan."
                ]
            },
            'en': {
                'prefix': [
                    "I'm sorry, ",
                    "I understand your confusion. ",
                    "Let me try to explain again, "
                ],
                'suffix': [
                    " Hope this helps.",
                    " Is this explanation clear enough?",
                    " Let me know if anything is still unclear."
                ]
            }
        },
        'very_negative': {
            'id': {
                'prefix': [
                    "Aku sangat minta maaf, ",
                    "Mohon maaf atas ketidaknyamanannya. ",
                    "Aku mengerti kekecewaanmu. "
                ],
                'suffix': [
                    " Aku akan berusaha lebih baik.",
                    " Bagaimana aku bisa membantu memperbaiki ini?",
                    " Mari kita cari solusi bersama."
                ]
            },
            'en': {
                'prefix': [
                    "I sincerely apologize, ",
                    "I'm really sorry for the inconvenience. ",
                    "I understand your disappointment. "
                ],
                'suffix': [
                    " I'll do my best to make it right.",
                    " How can I help improve this situation?",
                    " Let's work together to find a solution."
                ]
            }
        }
    }

    # Respons untuk situasi khusus
    SPECIAL_RESPONSES = {
        'greeting': {
            'morning': {
                'id': "Selamat pagi! Cerbi siap membantu kamu hari ini! 🌅",
                'en': "Good morning! Cerbi's ready to help you today! 🌅"
            },
            'afternoon': {
                'id': "Selamat siang! Cerbi di sini, mau bantuin apa nih? ☀️",
                'en': "Good afternoon! Cerbi here, what can I help you with? ☀️"
            },
            'evening': {
                'id': "Selamat malam! Cerbi masih semangat buat bantu kamu! 🌙",
                'en': "Good evening! Cerbi's still energetic to help you! 🌙"
            }
        },
        'farewell': {
            'id': {
                'positive': "Cerbi senang bisa bantu! Sampai ketemu lagi ya! 👋✨",
                'neutral': "Makasih udah ngobrol sama Cerbi! Sampai jumpa! 👋",
                'negative': "Cerbi akan belajar lebih baik lagi! Sampai jumpa! 👋"
            },
            'en': {
                'positive': "Cerbi's glad to help! See you next time! 👋✨",
                'neutral': "Thanks for chatting with Cerbi! Goodbye! 👋",
                'negative': "Cerbi will learn to do better! Goodbye! 👋"
            }
        }
    }

    # Tambahkan identitas AI
    AI_IDENTITY = {
        'name': 'Cerbi',
        'id': {
            'introduction': '''
            Hai! Aku Cerbi, asisten virtual yang siap membantumu menjelajahi galeri foto ini. 
            Aku bisa membantu kamu mencari foto, menunjukkan kategori yang menarik, 
            dan menjawab pertanyaan-pertanyaan seputar galeri ini! 😊
            ''',
            'personality': 'ramah dan ceria'
        },
        'en': {
            'introduction': '''
            Hi! I'm Cerbi, a virtual assistant ready to help you explore this photo gallery. 
            I can help you find photos, show you interesting categories, 
            and answer any questions about the gallery! 😊
            ''',
            'personality': 'friendly and cheerful'
        }
    }

    # Template respons dinamis
    DYNAMIC_RESPONSES = {
        'popular_photos': {
            'id': 'Nih, foto-foto yang lagi hits banget! 🔥\n\n{photos_list}\n\nKeren kan? Mau lihat yang lainnya? 😊',
            'en': 'Check out these trending photos! 🔥\n\n{photos_list}\n\nPretty awesome, right? Want to see more? 😊'
        }
    }

    @classmethod
    def get_response(cls, intent, language):
        """Mendapatkan respons berdasarkan intent dan bahasa"""
        if intent in cls.RESPONSES and language in cls.RESPONSES[intent]:
            return cls.RESPONSES[intent][language]['text'].strip()
        return cls.GENERAL_RESPONSES['not_understood'][language]

    @classmethod
    def get_suggested_questions(cls, language):
        """Mendapatkan daftar pertanyaan yang disarankan"""
        return cls.SUGGESTED_QUESTIONS.get(language, cls.SUGGESTED_QUESTIONS['en'])

    @classmethod
    def get_error_response(cls, language):
        """Mendapatkan respons error"""
        return cls.GENERAL_RESPONSES['error'][language]

    @classmethod
    def get_emotional_response(cls, text, sentiment, language):
        """Mendapatkan respons dengan emosi yang sesuai"""
        # Tentukan level emosi
        emotion_level = 'neutral'
        for level, ratings in cls.EMOTION_LEVELS.items():
            if sentiment['label'] in ratings:
                emotion_level = level
                break

        # Ambil ekspresi emosi yang sesuai
        expressions = cls.EMOTIONAL_EXPRESSIONS[emotion_level][language]

        # Pilih prefix dan suffix secara random
        prefix = random.choice(expressions['prefix'])
        suffix = random.choice(expressions['suffix'])

        return f"{prefix}{text}{suffix}"

    @classmethod
    def get_introduction(cls, language):
        """Mendapatkan perkenalan Cerbi"""
        return cls.AI_IDENTITY[language]['introduction'].strip()

    @classmethod
    def get_greeting(cls, time_of_day, language):
        """Mendapatkan respons salam berdasarkan waktu hari"""
        if 'greeting' in cls.SPECIAL_RESPONSES and time_of_day in cls.SPECIAL_RESPONSES['greeting']:
            return cls.SPECIAL_RESPONSES['greeting'][time_of_day][language]
        # Default greeting
        greetings = cls.GENERAL_RESPONSES['greeting'][language]
        return random.choice(greetings)

    @classmethod
    def get_farewell(cls, sentiment, language):
        """Mendapatkan respons perpisahan berdasarkan emosi"""
        if 'farewell' in cls.SPECIAL_RESPONSES and sentiment in cls.SPECIAL_RESPONSES['farewell']:
            return cls.SPECIAL_RESPONSES['farewell'][language][sentiment]
        # Default farewell
        return "Sampai jumpa lagi! 👋" if language == 'id' else "Goodbye! 👋"

    @classmethod
    def get_dynamic_response(cls, intent, language, **kwargs):
        """Mendapatkan respons dinamis berdasarkan intent"""
        if intent in cls.DYNAMIC_RESPONSES and language in cls.DYNAMIC_RESPONSES[intent]:
            template = cls.DYNAMIC_RESPONSES[intent][language]
            return template.format(**kwargs)
        return cls.GENERAL_RESPONSES['not_understood'][language]
