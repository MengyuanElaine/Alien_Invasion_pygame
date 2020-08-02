import sys
import pygame
from bullt import Bullet
from alien import Alien
from time import sleep
from life import Life

#1. 键盘控制，游戏开始，图像移动等操作#
def check_events(ai_settings,screen,stats,play_button,ship,aliens,bullets,sb):
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            file=open("high_score_history.txt","w")
            file.write(str(stats.high_score))
            pygame.quit()
            sys.exit()
        elif event.type==pygame.KEYDOWN:
            #当按下键盘时如何反应#
            check_keydown_events(event,ai_settings,screen,stats,ship,
                                 aliens,bullets,sb)
        elif event.type==pygame.KEYUP:
            #当弹起键盘时如何反应#
            check_keyup_events(event,ship)
        elif event.type==pygame.MOUSEBUTTONDOWN:
            #当点击鼠标#
            mouse_x,mouse_y=pygame.mouse.get_pos()
            check_play_button(ai_settings,screen,stats,play_button,ship,aliens,
                      bullets,mouse_x,mouse_y,sb)

#1.1 键盘按下中分为左右空格键，(1)左右键触发小船移动，将移动位置储存在update中，在最后屏幕更新中调用#
#(2)按下空格键即生成新子弹#
            
def check_keydown_events(event,ai_settings,screen,stats,ship,aliens,bullets,sb):
    if event.key==pygame.K_RIGHT:
        ship.moving_right=True
    elif event.key==pygame.K_LEFT:
        ship.moving_left=True
    elif event.key==pygame.K_SPACE:
        fire_bullet(ai_settings,screen,ship,bullets)
    elif event.key==pygame.K_q:
        pygame.quit()
        sys.exit()
    elif event.key==pygame.K_p:
        if not stats.game_active:
            start_game(ai_settings,screen,stats,ship,aliens,bullets,sb)
            ai_settings.initialize_dynamic_settings()
            
#1.1.3 按下空格，检查屏幕中的子弹是否小于/等于3个，如果是，则添加新的子弹，储存在Group中#
def fire_bullet(ai_settings,screen,ship,bullets):
    if len(bullets)<ai_settings.bullet_allowed:
        new_bullet=Bullet(ai_settings,screen,ship)
        bullets.add(new_bullet)

#1.2 键盘弹起时飞船移动为False#
def check_keyup_events(event,ship):
    if event.key==pygame.K_RIGHT:
        ship.moving_right=False
    elif event.key==pygame.K_LEFT:
        ship.moving_left=False


#2. 用update更新每个子弹的位置，当其超出屏幕则移除，没有超出则更新到屏幕#
def update_bullets(ai_settings,screen,ship,aliens,bullets,stats,sb):
    bullets.update()
    for bullet in bullets.copy():
        if bullet.rect.bottom<=0:
            bullets.remove(bullet)

    #建立子弹和外星人相撞函数，先建造能自动移动的外星人吧#
    check_bullet_alien_collision(ai_settings,screen,ship,aliens,bullets,stats,sb)

#3. 自动移动的外星人#
#3.1 首先在游戏最前面设置一群外星人#
def creat_fleet(ai_settings,screen,ship,aliens):
    alien=Alien(ai_settings,screen)
    #定义外星人的位置，多少，需要先以一个外星人为模板，调用它的数据#
    number_alien_x=get_number_aliens_x(ai_settings,alien.rect.width)
    number_rows=get_number_rows(ai_settings,ship.rect.height,alien.rect.height)
    for row_number in range(number_rows):
        for alien_number in range(number_alien_x):
            #在一行中一列建立一个外星人，通过for循环，不断添加#
            creat_alien(ai_settings,screen,aliens,alien_number,row_number)

#3.2 定义每行可以容纳多少外星人#
def get_number_aliens_x(ai_settings,alien_width):
    available_space_x=ai_settings.screen_width - 4*alien_width
    number_aliens_x=int(available_space_x/(2*alien_width))
    return number_aliens_x

#3.3 定义需要几列#
def get_number_rows(ai_settings,ship_height,alien_height):
    avalible_space_y=ai_settings.screen_height-(3*alien_height)-(ship_height)
    number_rows=int(avalible_space_y/(2*alien_height))
    return number_rows

#3.4 每行每列建造一个外星人，添加其到Group中#
def creat_alien(ai_settings,screen,aliens,alien_number,row_number):
    alien=Alien(ai_settings,screen)
    alien_width=alien.rect.width
    alien.x=alien_width+2*alien_width*alien_number
    alien.rect.x=alien.x
    alien.rect.y=alien.rect.height+3*alien.rect.height*row_number
    aliens.add(alien)

#4. 所有外星人都添加至Group中，需要让其动起来，且检查其位置#
def update_aliens(ai_settings,stats,screen,ship,aliens,bullets,sb):
    check_fleet_edges(ai_settings,aliens)
    #检查没碰壁或已经更新方向后的aliens全部更新位置#
    aliens.update()
    #当ship和外星人相撞，则需要重启游戏#
    if pygame.sprite.spritecollideany(ship,aliens):
        #如果游戏次数<0，游戏结束；游戏次数>0，游戏重启#
        ship_hit(ai_settings,stats,screen,ship,aliens,bullets,sb)
     #如果外星人触碰屏幕底，也重启游戏#   
    check_aliens_bottom(ai_settings,stats,screen,ship,aliens,bullets,sb)

#4.1 在aliens.update()更新其位置时，需要检查是否碰到壁了，如果碰壁则改变方向#
def check_fleet_edges(ai_settings,aliens):
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings,aliens)
            #只要循环中有一个元素碰壁就开始转换方向，因此循环结束，需要break#
            break
        

#4.1.1 碰壁后怎么办？方向变为-1,且下落一格，再碰壁则再*-1变为正数#
def change_fleet_direction(ai_settings,aliens):
    for alien in aliens.sprites():
        alien.rect.y+=ai_settings.fleet_drop_speed
    ai_settings.fleet_direction*=-1

#4.1.2 外星人触底后也要丧失一条生命，游戏重新开始#
def check_aliens_bottom(ai_settings,stats,screen,ship,aliens,bullets,sb):
    screen_rect=screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom>=screen_rect.bottom:
            ship_hit(ai_settings,stats,screen,ship,aliens,bullets,sb)
            break
            
#子弹打中外星人，如果外星人全部覆灭，则游戏重新开始，速度/等级增加#
#统计总分=子弹打中外形人的个数*分数#
def check_bullet_alien_collision(ai_settings,screen,ship,aliens,bullets,stats,sb):
    collisions=pygame.sprite.groupcollide(bullets,aliens,True,True)
    start_new_level(ai_settings,screen,ship,aliens,bullets,stats,sb)
    if collisions:
        for aliens in collisions.values():
            stats.score+=ai_settings.alien_points*len(aliens)
            sb.prep_score()
        check_high_score(stats,sb)

def start_new_level(ai_settings,screen,ship,aliens,bullets,stats,sb):
    if len(aliens)==0:
        bullets.empty()
        ai_settings.increase_speed()
        stats.level+=1
        sb.prep_level()
        creat_fleet(ai_settings,screen,ship,aliens)


#更新最高分#
def check_high_score(stats,sb):
    if stats.score>stats.high_score:
        stats.high_score=stats.score
        sb.prep_high_score()

#重启后初始化#
def check_play_button(ai_settings,screen,stats,play_button,ship,aliens,
                      bullets,mouse_x,mouse_y,sb):
    button_clicked=play_button.rect.collidepoint(mouse_x,mouse_y)
    if button_clicked and not stats.game_active:
        start_game(ai_settings,screen,stats,ship,aliens,bullets,sb)
        ai_settings.initialize_dynamic_settings()
        

def start_game(ai_settings,screen,stats,ship,aliens,bullets,sb):
    pygame.mouse.set_visible(False)
    check_history_score(stats)
    stats.reset_stats()
    stats.game_active=True
    sb.prep_score()
    sb.prep_high_score()
    sb.prep_level()
    sb.prep_lives()

    

    aliens.empty()
    bullets.empty()
    creat_fleet(ai_settings,screen,ship,aliens)
    ship.center_ship()


def check_history_score(stats):
    file=open("high_score_history.txt","r")
    history_score=int(file.read())
    if history_score<stats.high_score:
        file=open("high_score_history.txt","w")
        file.write(str(stats.high_score))
    return history_score
    
        
#重启游戏，当生命>0时，更新所有图像画面，休眠0.5s继续开始；生命<0时，则显示Play按键#
def ship_hit(ai_settings,stats,screen,ship,aliens,bullets,sb):
    #当游戏次数>0时，减少一次机会#
    if stats.ship_left>0:
        stats.ship_left-=1
        sb.prep_lives()
        aliens.empty()
        bullets.empty()

        creat_fleet(ai_settings,screen,ship,aliens)
        ship.center_ship()

        sleep(0.5)
    else:
        #当游戏次数==0时，则终止游戏，Play按键弹出，控制游戏开始的终极指令stats.game_active为Fasle#
        stats.game_active=False
        #屏幕上显示鼠标#
        pygame.mouse.set_visible(True)


#将图像上传至屏幕上，且更新屏幕#
def update_screen(ai_settings,screen,stats,ship,aliens,bullets,play_button,sb):
    screen.fill(ai_settings.bg_color)
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)
    sb.show_score()
    if not stats.game_active:
        play_button.draw_button()
    pygame.display.flip()
