# Keep php 8.2-fpm base
FROM php:8.2-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git curl zip unzip supervisor \
    libpq-dev \
    && docker-php-ext-install pdo_pgsql sockets \
    && pecl install redis \
    && docker-php-ext-enable redis

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Create non-root user
RUN useradd -m appuser && mkdir -p /var/www && chown -R appuser:www-data /var/www

WORKDIR /var/www

# Copy application as appuser
COPY --chown=appuser:www-data . .

# Install PHP dependencies as appuser
USER appuser
RUN composer install --no-dev --optimize-autoloader

# Create storage directories
RUN mkdir -p storage/logs storage/framework/cache storage/framework/sessions storage/framework/views \
    && chmod -R 775 storage

# Copy supervisor config
USER root
COPY supervisord.conf /etc/supervisor/conf.d/

# Expose port
EXPOSE 9000

# Run supervisord as root (so pidfile is writable)
CMD ["/usr/bin/supervisord", "-n"]
