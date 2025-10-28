
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'i1u63^ba=6#vzc_0t6m_!m$)iejuq@v9!6dqq!jgzpkj=^9#t2'

DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'corsheaders',  # Thêm dòng này
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Thêm dòng này lên trên cùng
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CHATBOT_WEB.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['CHATBOT_WEB/Views',]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CHATBOT_WEB.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
# Thêm biến này vào cuối file, thay bằng địa chỉ website của bạn
CORS_ALLOWED_ORIGINS = [
    # "http://your-website.com",
    # "https://your-website.com",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080", # Thêm cả địa chỉ này để chắc chắn
    "http://127.0.0.1:5501", # Thêm dòng này nếu bạn test bằng Live Server của VS Code
    "null", # Cho phép test từ file HTML mở trực tiếp
]
# CẢNH BÁO: Chỉ dùng cho môi trường phát triển, không nên dùng khi triển khai thực tế.
CORS_ALLOW_ALL_ORIGINS = True 