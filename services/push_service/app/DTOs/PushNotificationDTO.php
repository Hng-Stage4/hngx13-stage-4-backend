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
        $template = $data['template'] ?? [];
        $variables = $data['variables'] ?? [];
        $delivery = $data['delivery'] ?? [];
        
        $title = $template['title'] ?? $template['subject'] ?? '';
        $body = $template['body'] ?? '';
        
        $body = strip_tags($body);
        
        foreach ($variables as $key => $value) {
            if (is_string($value)) {
                $placeholder = '{{'.$key.'}}';
                $title = str_replace($placeholder, $value, $title);
                $body = str_replace($placeholder, $value, $body);
            }
        }
        
        if (empty($title)) {
            $title = 'New Notification';
        }
        
        $pushToken = $delivery['push_token'] ?? '';
        
        if (empty($pushToken)) {
            throw new \InvalidArgumentException('push_token is required in delivery object');
        }
        
        if (empty($data['notification_id'])) {
            throw new \InvalidArgumentException('notification_id is required');
        }
        
        $link = $variables['link'] ?? null;
        
        return new self(
            notification_id: $data['notification_id'],
            user_id: $data['user_id'],
            push_token: $pushToken,
            title: $title,
            body: $body,
            image: $template['image'] ?? null,
            link: $link,
            data: $data['metadata'] ?? null,
            priority: $data['priority'] ?? 1,
            request_id: $data['request_id'] ?? null,
        );
    }
}