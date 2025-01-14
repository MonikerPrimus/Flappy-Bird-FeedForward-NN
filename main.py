import pygame
import neat
import os
import random

# initilize

pygame.init()
pygame.font.init()

pygame.display.set_caption("Flappy Bird")
icon = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bird1.png")), (45,32))
pygame.display.set_icon(icon)

WIN_WIDTH = 400
WIN_HEIGHT = 550
GEN = 0
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

#imgs
pipe_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha(), (69,400))
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (400, 700))
bird_imgs = [pygame.transform.scale(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png")), (45,32)) for x in range(1,4)]
base_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha(), (449,149))

STAT_FONT = pygame.font.SysFont("comicsans",33)

# classes

class Bird:
    IMGS = bird_imgs
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
            d = 16
        if d <= 0:
            d -=2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt-= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 133
    VEL = 5
    def __init__(self,x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(33, 300)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self,win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win,birds,pipes,base,score,gen):
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render(f"Score: {score}", True, (255,255,255))
    win.blit(text, (WIN_WIDTH-6-text.get_width(),6))

    text = STAT_FONT.render(f"Gen: {GEN}", True, (255,255,255))
    win.blit(text, (10,10))

    score_label = STAT_FONT.render("Alive: " + str(len(birds)),True,(255,255,255))
    win.blit(score_label, (10, 40))

    for bird in birds:
        bird.draw(win)
    base.draw()
    pygame.display.update()

def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []
    for _, g in genomes:
        g.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(156,233))
        ge.append(g)


    bird = Bird(156,233)
    base = Base(486)
    pipes = [Pipe(500)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    clock = pygame.time.Clock()
    score = 0
    add_pipe = False



    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        #bird.move()
        base.move()

        rem = []

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break


        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        for pipe in pipes:
            for x, bird in enumerate(birds):

                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)



                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(500))
            add_pipe = False

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 500 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(win,birds,pipes,base,score,GEN)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)

