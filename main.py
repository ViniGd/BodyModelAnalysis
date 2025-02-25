# Importa as bibliotecas necessárias
import trimesh
import numpy as np
import imageio
import zipfile
import pandas as pd
import os
import gc
import plotly.graph_objects as go
from IPython.display import Image

# Definindo funções
# Função para carregar e visualizar o arquivo STL
def LoadAndVisualizeSTL(file_path, label):
    # Leitura do arquivo STL
    mesh = trimesh.load_mesh(file_path, enable_post_processing=True, solid=True)
    # Extrair vértices e faces
    vertices = mesh.vertices
    faces = mesh.faces
    # Criar uma lista de vértices para cada face
    face_vertices = [vertices[face] for face in mesh.faces]
    # Converter a lista para um array NumPy e depois para DataFrame do pandas
    face_vertices_np = np.array(face_vertices)
    faces_df = pd.DataFrame(face_vertices_np.reshape(-1, 3), columns=['X', 'Y', 'Z'])
    # Adicionar um índice multi-nível para identificar cada face
    faces_df.index = pd.MultiIndex.from_product([range(1, len(mesh.faces) + 1), ['Vértice 1', 'Vértice 2', 'Vértice 3']], names=['Face', 'Ponto'])
    return mesh

# Função para visualizar o arquivo STL usando Plotly
def VisualizeNew(file_path, label):
    # Leitura do arquivo STL
    mesh = trimesh.load_mesh(file_path, enable_post_processing=True, solid=True)
    # Extrair vértices e faces
    vertices = mesh.vertices
    faces = mesh.faces
    # Criar uma figura Plotly
    fig = go.Figure(data=[go.Mesh3d(x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2], i=faces[:, 0], j=faces[:, 1], k=faces[:, 2], color='lightblue', opacity=0.70)])
    # Ajustar layout da figura
    fig.update_layout(title='Faces from: '+ label+'.stl', width=800, height=600, scene=dict(xaxis=dict(title='X'), yaxis=dict(title='Y'), zaxis=dict(title='Z')))
    # Mostrar a figura
    fig.show()

# Função para criar uma animação GIF da grade de voxels
def CreateVoxelAnimation(voxel_data, filename, report_folder):
    images = []
    max_index = min(voxel_data.shape[0], voxel_data.shape[2])
    for i in range(max_index):
        image = (voxel_data[:, :, i] * 255).astype(np.uint8)
        images.append(image)
    # Salvar o GIF diretamente na pasta Report
    gif_path = os.path.join(report_folder, filename + '.gif')
    imageio.mimsave(gif_path, images, fps=100, loop=0)
    return gif_path

# Função para criar e salvar o arquivo ZIP contendo o GIF e o relatório TXT
def DownloadZip(filename, myobj, report_folder):
    # Criar o arquivo TXT
    txt_path = criar_arquivo_txt(filename, myobj, report_folder)
    # Criar o arquivo GIF
    gif_path = os.path.join(report_folder, filename + '.gif')
    # Caminho completo para o arquivo ZIP
    zip_filename = os.path.join(report_folder, filename + '.zip')
    # Criar o arquivo ZIP contendo o GIF e o TXT
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(gif_path, arcname=filename + '.gif')
        zipf.write(txt_path, arcname='Relatorio_'+filename + '.txt')
    print(f"Arquivo ZIP salvo em: {zip_filename}")
    # Excluir arquivos temporários (GIF e TXT)
    os.remove(gif_path)
    os.remove(txt_path)
    print(f"Arquivos temporários excluídos: {gif_path}, {txt_path}")

def criar_arquivo_txt(filename, myobj, report_folder):
    # Nome do arquivo seguindo o padrão
    nome_arquivo = f'Relatorio_{filename}.txt'
    # Conteúdo do relatório
    conteudo = f"""
    Analisando: {filename}
    -----------------------------------------
    Caracteristicas físicas
    -----------------------------------------
    Volume: {myobj.volume:.2f} U³ ({myobj.volume})
    -----------------------------------------
    Área: {myobj.area:.2f} U² ({myobj.area})
    -----------------------------------------
    Massa: {myobj.mass:.2f} kg
    -----------------------------------------
    Densidade: {myobj.density:.2f} kg/m³
    -----------------------------------------
    Caracteristicas geométricas
    -----------------------------------------
    Faces: {myobj.faces.shape[0]}
    -----------------------------------------
    Vertices: {myobj.vertices.shape[0]}
    -----------------------------------------
    Voxels preenchidos: {filled_voxels}
    -----------------------------------------
    """
    # Caminho do arquivo
    caminho_arquivo = os.path.join(report_folder, nome_arquivo)
    # Criar e escrever no arquivo
    with open(caminho_arquivo, 'w') as file:
        file.write(conteudo)
    return caminho_arquivo

def limpar_variaveis(*variaveis):
    for variavel in variaveis:
        if variavel in globals():
            del globals()[variavel]

# Definindo variáveis
i = 0
nomes = []

# Caminho para a pasta STL
stl_folder = './STL'

# Caminho para a pasta Report
report_folder = './Report'
# Criar a pasta Report se não existir
if not os.path.exists(report_folder):
    os.makedirs(report_folder)

# Listar todos os arquivos na pasta STL
file_paths = [os.path.join(stl_folder, f) for f in os.listdir(stl_folder) if f.endswith('.stl')]

print("Quantidade de itens encontrados: "+ str(len(file_paths)))
print("-----------------------------------------")

# Exibir a lista de caminhos dos arquivos
print("Arquivos encontrados:")
# Ordenar em ordem alfabética
file_paths.sort()
for path in file_paths:
    # Extrair o nome do arquivo sem a extensão
    nome_arquivo = os.path.basename(path).replace('.stl', '')
    nomes.append(nome_arquivo)
    print(str(i) +": "+ nome_arquivo)
    i += 1
print("-----------------------------------------")

item = int(input("Escolha um arquivo: "))

# Definir resolução da grade de voxels
voxel_resolution = 100  # Aumentar para maior resolução, diminuir para menor resolução

# Carregar e visualizar o arquivo STL selecionado
myobj = LoadAndVisualizeSTL(file_paths[item], nomes[item])

# Converter a malha para uma grade de voxels
voxel_grid = myobj.voxelized(pitch=myobj.bounding_box.extents.min() / voxel_resolution)
voxel_data = voxel_grid.matrix

# Contar o número de voxels preenchidos
filled_voxels = np.sum(voxel_data)

# Criar animação GIF da grade de voxels
gif_path = CreateVoxelAnimation(voxel_data, nomes[item], report_folder)

# Criar e salvar o arquivo ZIP contendo o GIF e o relatório TXT
DownloadZip(nomes[item], myobj, report_folder)

# Visualizar o arquivo STL usando Plotly
VisualizeNew(file_paths[item], nomes[item])

# Forçar a coleta de lixo
gc.collect()