import pygame
import os
import math
import random

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width, screen_height = 1600, 1200
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("이동하는 플레이어")

# 플레이어 이미지 로드 및 크기 조정
current_path = os.path.dirname(__file__)  # 현재 파일의 경로
player_image = pygame.image.load(os.path.join(current_path, 'public', 'player', 'gun.png'))
player_image = pygame.transform.scale(player_image, (50, 50))  # 크기 조정
player_original = player_image.copy()  # 원본 이미지 복사
player_rect = player_image.get_rect()
player_rect.center = (screen_width // 2, screen_height // 2)

# 장애물 이미지 로드 및 크기 조정
obstacle_image = pygame.image.load(os.path.join(current_path, 'public', 'building', 'roof.png')).convert_alpha()
obstacle_image = pygame.transform.scale(obstacle_image, (50, 50))  # 크기 조정
obstacle_original = obstacle_image.copy()  # 원본 이미지 복사

# 장애물 생성 (플레이어 위치와 비슷한 크기로 조정)
obstacle_list = []
while len(obstacle_list) < 10:  # 장애물 개수를 조절할 수 있습니다. 이 예제에서는 10개로 설정하겠습니다.
    obstacle_rect = pygame.Rect(random.randint(0, screen_width - 50), random.randint(0, screen_height - 50), 50, 50)
    distance = math.hypot(obstacle_rect.centerx - player_rect.centerx, obstacle_rect.centery - player_rect.centery)
    if distance > 150:  # 플레이어와 장애물 간의 최소 거리 설정 (150 픽셀)
        obstacle_list.append(obstacle_rect)

# 초기 각도 설정
angle = 0

clock = pygame.time.Clock()
running = True
while running:
    screen.fill((255, 255, 255))  # 흰 배경

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    x_change, y_change = 0, 0

    if keys[pygame.K_LEFT]:
        x_change -= 5
    if keys[pygame.K_RIGHT]:
        x_change += 5
    if keys[pygame.K_UP]:
        y_change -= 5
    if keys[pygame.K_DOWN]:
        y_change += 5

    # 플레이어의 이동 방향으로 회전각을 계산합니다.
    if x_change != 0 or y_change != 0:
        angle = math.degrees(math.atan2(y_change, x_change))
        new_rect = player_rect.move(x_change, y_change)

        # 모든 장애물과의 충돌 체크
        collision = False
        for obstacle_rect in obstacle_list:
            if new_rect.colliderect(obstacle_rect):
                collision = True
                break

        # 충돌하지 않을 때만 이동
        if not collision:
            player_rect = new_rect

    # 이미지 회전을 위한 작업
    angle %= 360  # 각도를 0에서 360도 사이로 정규화
    rotated_image = pygame.transform.rotate(player_original, angle)
    rotated_rect = rotated_image.get_rect(center=player_rect.center)

    # 화면에 모든 장애물 이미지 그리기
    for obstacle_rect in obstacle_list:
        screen.blit(obstacle_image, obstacle_rect)

    # 화면에 플레이어 이미지 그리기
    screen.blit(rotated_image, rotated_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()