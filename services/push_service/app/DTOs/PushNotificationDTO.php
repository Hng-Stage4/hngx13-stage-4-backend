<?php

namespace App\DTOs;

class PushNotificationDTO
{
    public function __construct(
        public string $notification_id,
        public string $user_id,
        public string $push_token,
        public string $title,
        public string $body,
        public ?string $image = null,
        public ?string $link = null,
        public ?array $data = null,
        public int $priority = 1,
        public ?string $request_id = null,
    ) {}

    public static function fromArray(array $data): self
    {
        return new self(
            notification_id: $data['notification_id'],
            user_id: $data['user_id'],
            push_token: $data['push_token'],
            title: $data['title'],
            body: $data['body'],
            image: $data['image'] ?? null,
            link: $data['link'] ?? null,
            data: $data['data'] ?? null,
            priority: $data['priority'] ?? 1,
            request_id: $data['request_id'] ?? null,
        );
    }
}