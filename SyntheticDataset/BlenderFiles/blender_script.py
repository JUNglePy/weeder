import bpy
import random
from mathutils import Euler
import numpy as np
from mathutils import Vector, Matrix
from math import cos, sin, pi
from mathutils import Vector
import csv


# Устанавливаем количество итераций
num_iterations = 5000
output_directory = "D:/Projects/Automation/DS/Datasets/blender_plants/dataset/"
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512


# Создаем CSV файл для сохранения данных
csv_filepath = output_directory + "cylinder_bboxes.csv"
#with open(csv_filepath, 'w', newline='') as file:
#    writer = csv.writer(file)
#    writer.writerow(["ImageNumber", "MinX", "MinY", "MaxX", "MaxY"])


for iteration in range(0, num_iterations + 1):
    print(f'iteration: {iteration}')
    # Path to the .blend file with the earth model
    path_to_ground_blend = "D:/Projects/Automation/DS/Datasets/blender_plants/dandelion/Dandelion_blend/ground_model_v1.blend"  # Replace with the path to your .blend file

    # Import the earth model from the .blend file
    with bpy.data.libraries.load(path_to_ground_blend) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name.startswith("ground")]


    # Create an instance of the earth model
    ground = data_to.objects[0]
    bpy.context.collection.objects.link(ground)


    # Apply modifiers for a smooth surface
    bpy.context.view_layer.objects.active = ground
    ground.select_set(True)
    bpy.ops.object.shade_smooth()

    # Apply all modifiers
    bpy.ops.object.convert(target='MESH')

    # Create a noise texture
    noise_texture = bpy.data.textures.new("NoiseTexture", 'CLOUDS')

    # Configure noise texture parameters
    noise_texture.noise_scale = 0.1  # Change this parameter to adjust the scale of the noise

    # Create a Displace modifier
    bpy.ops.object.modifier_add(type='DISPLACE')
    displace_modifier = ground.modifiers["Displace"]
    displace_modifier.strength = 0.05 # Уменьшить силу смещения

    # Apply the noise texture as a displacement source for the Displace modifier
    displace_modifier.texture = noise_texture

    bpy.ops.object.modifier_apply({"object": ground}, modifier=displace_modifier.name)
    bpy.ops.object.shade_smooth()


    ##DANDELION

    # Функция копирования иерархии объектов
    def copy_object_hierarchy(obj, collection):
        new_obj = obj.copy()
        new_obj.data = obj.data.copy() if obj.data else None
        collection.objects.link(new_obj)
        for child in obj.children:
            new_child = copy_object_hierarchy(child, collection)
            new_child.parent = new_obj
        return new_obj


    # Функция для рандомизации цветка
    def randomize_model(model, size_min=0.4, size_max=1.2, max_del_parts=3, parts_size_diff=0.2, parts_rotate_diff=20):
        # Масштабирование модели
        scale_factor = random.uniform(size_min, size_max)
        model.scale = (scale_factor, scale_factor, scale_factor)
        
        # Вращение модели
        rotation_angle = random.uniform(0, 360)
        model.rotation_euler = Euler((0, 0, rotation_angle), 'XYZ')
        
        # Удаление подобъектов
        children = [child for child in model.children]
        random.shuffle(children)
        max_del_parts = random.randint(0, max_del_parts)  # изменение кол-ва удаляемых подобъектов
        for child in children[:max_del_parts]:
            bpy.data.objects.remove(child, do_unlink=True)
            
        # Условное удаление 'stern'
        
        # Условное удаление 'stern'
        rand_num_stern = random.random()
        stern_to_remove = (scale_factor < 0.8) or (rand_num_stern < 0.8)
        
        if stern_to_remove:
            for child in model.children:
                if child.name.startswith("stem"):
                    bpy.data.objects.remove(child, do_unlink=True)
                    break  # выход из цикла после удаления первого найденного 'stern'
        
        # Масштабирование и вращение подобъектов
        for child in model.children:
            child.scale.x *= random.uniform(1-parts_size_diff, 1+parts_size_diff)
            child.scale.y *= random.uniform(1-parts_size_diff, 1+parts_size_diff)
            child.rotation_euler = Euler((0, 0, random.uniform(-parts_rotate_diff, parts_rotate_diff)), 'XYZ')

            # Изменение цвета материала
    #        if child.data.materials:
    #            material = child.data.materials[0].copy()  # создание копии материала
    #            material.diffuse_color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)
    #            child.data.materials[0] = material  # применение нового материала


    # Загрузка dandelion
    # Путь к файлу модели
    filepath_dandelion = "D:/Projects/Automation/DS/Datasets/blender_plants/dandelion/Dandelion_blend/Dandelion_model_v2.blend"
    collection_name_dandelion = "Dandelion_col"

    # Импорт коwллекции
    with bpy.data.libraries.load(filepath_dandelion) as (data_from, data_to):
        data_to.collections = [name for name in data_from.collections if name == collection_name_dandelion]

    # Добавление коллекции в текущую сцену
    for coll in data_to.collections:
        if coll is not None:
            bpy.context.scene.collection.children.link(coll)

    # Загрузка radish
    filepath_radish = "D:/Projects/Automation/DS/Datasets/blender_plants/dandelion/Dandelion_blend/Radish_model_v3.blend"
    collection_name_radish = "Radish_col"

    with bpy.data.libraries.load(filepath_radish) as (data_from, data_to):
        data_to.collections = [name for name in data_from.collections if name == collection_name_radish]

    for coll in data_to.collections:
        if coll is not None:
            bpy.context.scene.collection.children.link(coll)



    def randomize_camera(camera, radius=2):
        # Выбор случайной позиции на окружности вокруг начала координат
        angle = random.uniform(0, 2 * pi)  # случайный угол в радианах
        x = radius * cos(angle)  # конвертация полярных координат в декартовы
        y = radius * sin(angle)
        z = random.uniform(0.3, 1.2)  # случайное значение по оси Z
        
        # Установка позиции камеры
        camera.location = (x, y, z)

        # Направление взгляда камеры к центру
        dir = Vector((0, 0, 0)) - camera.location
        rot_quat = dir.to_track_quat('-Z', 'Y')

        camera.rotation_euler = rot_quat.to_euler()

        # Добавление небольшого поворота
        camera.rotation_euler.x += random.uniform(-0.18, 0.18)  # примерно +/- 10 градусов
        camera.rotation_euler.y += random.uniform(-0.18, 0.18)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)




    def randomize_light(light):
        # Изменение положения освещения
        light.location.x += random.uniform(-1, 1)
        light.location.y += random.uniform(-1, 1)
        light.location.z += random.uniform(-1, 1)
            


    # Создание списков моделей
    n_dandelion = 10
    n_radish = 10

    models_list = ['dandelion']*n_dandelion  + ['radish']*n_radish
    random.shuffle(models_list)

    # Создание новых коллекций
    dandelion_collection_copy = bpy.data.collections.new('dandelion_copy')
    radish_collection_copy = bpy.data.collections.new('radish_copy')
    bpy.context.scene.collection.children.link(dandelion_collection_copy)
    bpy.context.scene.collection.children.link(radish_collection_copy)


    # Получение объекта dandelion в Dandelion_col и копирование его иерархии
    dandelion_obj = [obj for obj in bpy.data.collections['Dandelion_col'].objects if obj.name == 'dandelion'][0]
    radish_obj = [obj for obj in bpy.data.collections['Radish_col'].objects if obj.name == 'radish'][0]


    # Количество цветков и размер сетки
    n = n_dandelion + n_radish
    l = 0.4

    # Создание сетки
    size = 2*l
    grid = [(x, y, 0) for x in np.linspace(-size, size, int(2*size/l)) for y in np.linspace(-size, size, int(2*size/l))]


    # Случайное удаление точек
    random.shuffle(grid)
    grid = grid[:n]

    # Добавление случайного смещения и размещение цветков
    for i, (x, y, z) in enumerate(grid):
        dx, dy = random.uniform(-l/2, l/2), random.uniform(-l/2, l/2)
        model_choice = models_list.pop()
        if model_choice == 'dandelion':
            new_obj = copy_object_hierarchy(dandelion_obj, dandelion_collection_copy)
            
        else:
            new_obj = copy_object_hierarchy(radish_obj, radish_collection_copy)
        
        new_obj.location = Vector((x+dx, y+dy, z))

        # Рандомизация цветка
        
        if model_choice == 'radish':
            randomize_model(new_obj, size_min=0.3, size_max=1.2, max_del_parts=3, parts_size_diff=0.6, parts_rotate_diff=20)
        else:
            randomize_model(new_obj)

        # Вычисляем точку, где луч, исходящий из центра цветка, сталкивается с поверхностью
        location = new_obj.location
        location.z += 1  # Смещаем начальную точку на 1 метр вверх
        direction = Vector((0, 0, -1))
        result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, location, direction)

        if result:
            # Устанавливаем новую высоту цветка, чтобы она была на уровне поверхности
            new_obj.location.z = location.z


    # Использование функции randomize_camera
    camera = bpy.data.objects['Camera']
    randomize_camera(camera)

    # Использование функции randomize_light
    light = bpy.data.objects['Light']
    randomize_light(light)
    # Изменение интенсивности освещения
    if light.data.type == 'POINT':
        light.data.energy = random.uniform(3500, 5000)  # увеличиваем диапазон интенсивности
        
        


    # Скрыть всю коллекцию
    bpy.data.collections['Dandelion_col'].hide_viewport = True
    bpy.data.collections['Dandelion_col'].hide_render = True

    bpy.data.collections['Radish_col'].hide_viewport = True
    bpy.data.collections['Radish_col'].hide_render = True        
        

    ### Получаем координаты Boundary box за счет проекции на плоскость камеры
    from mathutils import Vector
    import bpy_extras

    def project_3d_to_2d(scene, cam, coord):
        """Проецирует 3D координаты на 2D плоскость камеры."""
        pr = bpy_extras.object_utils.world_to_camera_view(scene, cam, coord)
        render_scale = scene.render.resolution_percentage / 100
        render_size = (int(scene.render.resolution_x * render_scale), 
                       int(scene.render.resolution_y * render_scale))
        return (int(pr.x * render_size[0]), int(render_size[1] - pr.y * render_size[1]))

    scene = bpy.context.scene
    cam = bpy.data.objects['Camera']

    cylinder_bboxes_2d = []

    for obj in bpy.data.objects:
        # Проверяем, является ли объект цилиндром и родительским объектом
        if obj.type == 'MESH' and "dandelion" in obj.name or "radish" in obj.name:
            
            bbox = obj.bound_box
            projected_coords = [project_3d_to_2d(scene, cam, obj.matrix_world @ Vector(corner)) for corner in bbox]

            visible = False
            for coord in projected_coords:
                if 0 <= coord[0] <= scene.render.resolution_x and 0 <= coord[1] <= scene.render.resolution_y:
                    visible = True
                    break

            if not visible:
                continue

            min_x = min([coord[0] for coord in projected_coords])
            max_x = max([coord[0] for coord in projected_coords])
            min_y = min([coord[1] for coord in projected_coords])
            max_y = max([coord[1] for coord in projected_coords])

            cylinder_bboxes_2d.append((min_x, min_y, max_x, max_y))



    # Рендерим обычное изображение
    image_name = str(iteration).zfill(4)  # Создаем имя изображения с ведущими нулями
    bpy.context.scene.render.filepath = output_directory + image_name + "_original_image" +  ".png"
    bpy.ops.render.render(write_still=True)


    # Создание материалов
    # Создание черного материала
    black_material = bpy.data.materials.new(name="BlackMaterial")
    black_material.diffuse_color = (0, 0, 0, 1)

    # Создание белого материала
    white_material = bpy.data.materials.new(name="WhiteMaterial")
    white_material.diffuse_color = (1, 1, 1, 1)



    # Применяем черный материал ко всем объектам
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(black_material)

    # Применяем белый материал к цилиндрам
    cylinder_names = ['dandelion', 'radish']
    for name in cylinder_names:
        for obj in bpy.data.objects:
            if obj.name.startswith(name):
                obj.hide_render = False
                obj.data.materials.clear()
                obj.data.materials.append(white_material)

    # Установить рендер-движок на Workbench
    bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'

    # Настройки Workbench
    workbench = bpy.context.scene.display.shading
    workbench.light = 'FLAT'  # Плоское освещение без теней
    workbench.color_type = 'OBJECT'  # Цвета объектов определяются исходя из материала объекта
    bpy.context.scene.display.shading.color_type = 'MATERIAL'

    # Настройте ваш черный и белый материалы как ранее и примените их к нужным объектам.



    # Задаем путь для сохранения рендера с цилиндрами
    bpy.context.scene.render.filepath = output_directory + image_name + "_original_image_boundary" + ".png"
    bpy.ops.render.render(write_still=True)


    ## СЕГМЕНТАЦИЯ

    import bpy

    # Создаем красный и синий материалы
    red_material = bpy.data.materials.new(name="RedMaterial")
    red_material.diffuse_color = (1.0, 0.0, 0.0, 1.0)

    blue_material = bpy.data.materials.new(name="BlueMaterial")
    blue_material.diffuse_color = (0.0, 0.0, 1.0, 1.0)

    # Присваиваем материалы соответствующим объектам
    for obj in bpy.data.objects:
        if "dandelion" in obj.name:
            for child in obj.children:
                child.data.materials.clear()
                child.data.materials.append(red_material)
            obj.hide_render = True
        # Если это radish объект или его копия
        elif "radish" in obj.name:
            for child in obj.children:
                child.data.materials.clear()
                child.data.materials.append(blue_material)
            obj.hide_render = True

    # Сделать цилиндры невидимыми для рендера
    for obj in bpy.data.objects:
        if obj.name == 'radish' or obj.name.startswith('radish.') or obj.name == 'dandelion' or obj.name.startswith('dandelion.'):
            obj.hide_render = True

    bpy.context.scene.render.filepath = output_directory + image_name + "_original_image_0_segmentation" + ".png"
    bpy.ops.render.render(write_still=True)



    # Сохраняем данные cylinder_bboxes_2d в CSV файл
    with open(csv_filepath, 'a', newline='') as file:
        writer = csv.writer(file)
        for bbox in cylinder_bboxes_2d:
            writer.writerow([image_name, bbox[0], bbox[1], bbox[2], bbox[3]])



    # Очистка сцены
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512

    # Подчищаем, чтобы старые объекты и материалы не влияли на новые итерации
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

    for obj in bpy.data.objects:
        if obj.type not in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj)

    collections_to_remove = ['Dandelion_col', 'Radish_col', 'dandelion_copy', 'radish_copy']

    for col_name in collections_to_remove:
        if col_name in bpy.data.collections:
            bpy.data.collections.remove(bpy.data.collections[col_name])
            
    
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        bpy.data.textures.remove(block)

    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    
    for img in bpy.data.images:
        bpy.data.images.remove(img)



print('dataset ready')