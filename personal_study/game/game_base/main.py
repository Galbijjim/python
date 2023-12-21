import pygame
import sys
import os
import random

# Pygame 초기화
pygame.init()

# 화면 크기 설정
screen = pygame.display.set_mode((800, 600))

# 색깔 정의
black = (0, 0, 0)

# 배경 이미지 로드
current_path = os.path.dirname(__file__)
background = pygame.image.load(os.path.join(current_path, 'public/background/grass.png'))
background = pygame.transform.scale(background, (800, 600))

# 플레이어 이미지 로드 및 크기 조정
player_image = pygame.image.load(os.path.join(current_path, 'public/player/gun.png'))
player_image = pygame.transform.scale(player_image, (player_image.get_width() // 3, player_image.get_height() // 3))
player_rect = player_image.get_rect(center=(400, 300))

# 장애물 이미지 로드 및 크기 조정
obstacle_image = pygame.image.load(os.path.join(current_path, 'public/background/roof.png'))
obstacle_image = pygame.transform.scale(obstacle_image, (50, 50))

# 플레이어 이동 속도 설정
player_speed = 1

# 장애물 위치 랜덤 생성 함수
def create_random_obstacle():
    while True:
        x = random.randint(0, 750)
        y = random.randint(0, 550)
        obstacle_rect = obstacle_image.get_rect(x=x, y=y)
        if not obstacle_rect.colliderect(player_rect):
            return obstacle_rect

# 초기 장애물 생성
obstacle_rect = create_random_obstacle()

# 게임 루프
while True:
    # 배경 이미지 표시
    screen.blit(background, (0, 0))
    
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # 플레이어 이동 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_rect.x += player_speed
    if keys[pygame.K_UP]:
        player_rect.y -= player_speed
    if keys[pygame.K_DOWN]:
        player_rect.y += player_speed
    
    # 플레이어가 화면을 벗어나지 않도록 제한
    if player_rect.left < 0:
        player_rect.left = 0
    elif player_rect.right > 800:
        player_rect.right = 800
    if player_rect.top < 0:
        player_rect.top = 0
    elif player_rect.bottom > 600:
        player_rect.bottom = 600
    
    # 장애물 그리기
    screen.blit(obstacle_image, obstacle_rect)
    
    # 충돌 감지: 플레이어와 장애물이 겹치면 게임 종료
    if player_rect.colliderect(obstacle_rect):
        pygame.quit()
        sys.exit()
    
    # 플레이어 그리기
    screen.blit(player_image, player_rect)
    
    # 화면 업데이트
    pygame.display.update()
