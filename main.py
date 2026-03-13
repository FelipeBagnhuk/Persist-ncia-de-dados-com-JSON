import glob
import json
from datetime import datetime
import os
import re
from models import CreateSection, PageStatus, SectionType
import uuid
from fastapi import FastAPI

app = FastAPI()

page = {}

#Função de salvar snapshot

def save_snapshot(page_id):
    os.makedirs("snapshots", exist_ok=True)
    
    try:
        with open(f'page_{page_id}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_id = str(uuid.uuid4())[:8]  # Pega 8 primeiros chars
            snapshot_filename = f"snapshots/page-{page_id}-{snapshot_id}-{timestamp}.json"
            
            data['snapshot_id'] = snapshot_id
            
            with open(snapshot_filename, 'w', encoding='utf-8') as sf:
                json.dump(data, sf, indent=4, ensure_ascii=False)
            print(f" Snapshot salvo: {snapshot_filename} (ID: {snapshot_id})")
            
    except FileNotFoundError:
        print(f" Arquivo page_{page_id}.json não encontrado.")

# Criar seção (POST) - Cria uma página e salva em um arquivo JSON, dependendo do Status(draft, published)

@app.post("/create-section/")
async def create_section(section: CreateSection):
    page = section.model_dump() 
    if section.status == PageStatus.DRAFT:
        with open(f'draft_page_id{section.page_id}.json', 'w', encoding='utf-8') as f:
            json.dump(page, f, indent=4, ensure_ascii=False)
        print(f"Seção criada e salva em draft_page_id{section.page_id}.json")
    elif section.status == PageStatus.PUBLISHED:
        with open(f'published_page_id{section.page_id}.json', 'w', encoding='utf-8') as f:
            json.dump(page, f, indent=4, ensure_ascii=False)
        print(f"Seção criada e salva em published_page_id{section.page_id}.json")
    return {"status": "success", "page_id": section.page_id}

# create_section(id=1, page_id=1, type=SectionType.MENU_ICON_1, title="Página Teste", status=PageStatus.DRAFT, sections=["Menu-Icon_1"], dinamic_content="Home")

# create_section(id=2, page_id=1, type=SectionType.MENU_ICON_2, title="Página Teste 2", status=PageStatus.PUBLISHED, sections=["Menu-Icon_2"], dinamic_content="About")

# Criar seção (POST) - Cria uma página e salva em um arquivo JSON, dependendo do Status(draft, published)

def create_section(id, page_id, type, title, status, sections, dinamic_content, BaseModel=CreateSection):
    page = BaseModel(section_id=id, page_id=page_id, type=type, title=title, status=status, sections=sections, dinamic_content=dinamic_content).dict()
    if status == PageStatus.DRAFT:
        with open(f'draft_page_id{page_id}.json', 'w', encoding='utf-8') as f:
            json.dump(page, f, indent=4, ensure_ascii=False)
        print(f"Seção criada e salva em draft_page_id{page_id}.json")
    elif status == PageStatus.PUBLISHED:
        with open(f'published_page_id{page_id}.json', 'w', encoding='utf-8') as f:
            json.dump(page, f, indent=4, ensure_ascii=False)
        print(f"Seção criada e salva em published_page_id{page_id}.json")
    

# create_section(id=1, page_id=1, type=SectionType.MENU_ICON_1, title="Página Teste", status=PageStatus.DRAFT, sections=["Menu-Icon_1"], dinamic_content="Home")

# create_section(id=2, page_id=1, type=SectionType.MENU_ICON_2, title="Página Teste 2", status=PageStatus.PUBLISHED, sections=["Menu-Icon_2"], dinamic_content="About")

# Atualiza seção específica (PUT)

def update_section(id, page_id, type, title, status, sections, dinamic_content, BaseModel=CreateSection):
    page = BaseModel(section_id=id, page_id=page_id, type=type, title=title, status=status, sections=sections, dinamic_content=dinamic_content).dict()
    if status == PageStatus.DRAFT:
        with open(f'draft_page_id{page_id}.json', 'w', encoding='utf-8') as f:
            json.dump(page, f, indent=4, ensure_ascii=False)
        print(f"Seção atualizada e salva em draft_page_id{page_id}.json")
    elif status == PageStatus.PUBLISHED:
        with open(f'published_page_id{page_id}.json', 'w', encoding='utf-8') as f:
            json.dump(page, f, indent=4, ensure_ascii=False)
        print(f"Seção atualizada e salva em published_page_id{page_id}.json")


# update_section(id=1, page_id=1, type=SectionType.MENU_ICON_1, title="Página Teste", status=PageStatus.DRAFT, sections=["Menu-Icon_1"], dinamic_content="inicio")

# update_section(id=2, page_id=1, type=SectionType.MENU_ICON_2, title="Página Teste 2", status=PageStatus.PUBLISHED, sections=["Menu-Icon_2"], dinamic_content="About")

# Publicar página (POST)

def publish_page(page_id):
    sections = {}
    
    # Ignora page_X.json (evita loop infinito)
    for file in glob.glob("*.json"):
        if f"page_{page_id}.json" in file:
            continue  # Pula páginas já publicadas
            
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('page_id') == page_id:
                    section_id = data.get('section_id')
                    if section_id:  # Só se tiver section_id válido
                        section_type = f"Menu-Icon_{section_id}"
                        
                        # Prioriza PUBLISHED sobre DRAFT
                        if (section_type not in sections or 
                            data['status'] == PageStatus.PUBLISHED):
                            sections[section_type] = {
                                "dynamic_content": data.get('dinamic_content'),
                                "title": data.get('title')
                            }
        except:
            continue
    
    page_template = {
        "page_id": page_id,
        "status": "published",
        "published_at": datetime.now().isoformat(),
        "sections": {}
    }
    
    for section_type in SectionType:
        page_template["sections"][section_type.value] = sections.get(section_type.value)
    
    # Salva a página publicada
    with open(f'page_{page_id}.json', 'w', encoding='utf-8') as f:
        json.dump(page_template, f, indent=4, ensure_ascii=False)
    
    print(f" Página {page_id} publicada! {len(sections)} seções.")
    save_snapshot(page_id)
    return page_template

# publish_page(page_id=1)

# Lista seções de uma página (GET) - Faz a leitura de arquivo JSON e mostra conteúdo:

def list_sections(page_id):
    try:
        with open(f'page_{page_id}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f'Seções da página {page_id}:')
            for section_type, section_data in data['sections'].items():
                print(f'  - {section_type}: {section_data}')
        return data
    except FileNotFoundError:
        print(f"Página {page_id} não encontrada.")
        return None

# list_sections(page_id=1)

#Lista as páginas (GET)

def list_pages():
    pages = {}
    
    # Regex captura: page_1.json → page_id=1
    pattern = r'page_(\d+)\.json'
    
    for filename in glob.glob("page_*.json"):
        match = re.match(pattern, filename)
        if match:
            page_id = int(match.group(1))
            pages[page_id] = {
                "filename": filename,
                "published_at": datetime.fromtimestamp(os.path.getmtime(filename)).isoformat()
            }
    
    return sorted(pages.items())  

# print(f'Páginas: {list_pages()}')

# Previsão (Draft para quem posta, não salva no público, POST)



# Lista Snapshots (GET)

def list_snapshots():
    """Lista TODOS os snapshots (mesmo page_id diferente)"""
    todos_snapshots = []
    pattern = r'snapshots[\\\\/]page-(\d+)-(\d{8}_\d{6})\.json'
    
    for filename in glob.glob("snapshots/page-*.json"):
        match = re.match(pattern, filename)
        if match:
            page_id = int(match.group(1))
            timestamp = match.group(2)
            todos_snapshots.append({
                "page_id": page_id,
                "filename": filename,
                "timestamp": timestamp,
                "created_at": datetime.fromtimestamp(os.path.getmtime(filename)).isoformat()
            })
    return sorted(todos_snapshots, key=lambda x: x["created_at"], reverse=True)

def print_snapshots():
    snapshots = list_snapshots()
    print(f" SNAPSHOTS ENCONTRADOS ({len(snapshots)}):")
    print("-" * 60)
    
    if not snapshots:
        print("  Nenhum snapshot encontrado!")
        return
    
    for i, snap in enumerate(snapshots, 1):
        print(f"  {i}. Page ID: {snap['page_id']}")
        print(f" Timestamp: {snap['timestamp']}")
        print(f" Criado: {snap['created_at'][:19]}")
        print(f" Arquivo: {snap['filename'].split('\\\\')[-1]}")  
        print()

# print_snapshots()

#Restaura Snapshot (POST)

def restore_snapshot_by_id(snapshot_id):
    """Restaura snapshot usando só o ID de 8 caracteres"""
    encontrado = False
    
    # Procura o snapshot pelo ID no nome do arquivo
    for filename in glob.glob("snapshots/page-*.json"):
        if snapshot_id in filename:
            encontrado = True
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            page_id = data.get('page_id')
            pagina_destino = f'page_{page_id}.json'
            
            with open(pagina_destino, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f" Restaurado! ID {snapshot_id}")
            print(f" {filename} → {pagina_destino}")
            return True
    
    if not encontrado:
        print(f" Snapshot ID '{snapshot_id}' não encontrado!")
    return False


# restore_snapshot_by_id("f06c44ec") #Inserir ID do snapshot (sempre ao final)

#Apagar todos os JSON (apenas para qualidade de vida)

def clean_all_jsons():
    """Exclui TODOS os arquivos .json do projeto (principal + snapshots)"""
    delete_json = []
    for arquivo in glob.glob("**/*.json", recursive=True):
        try:
            os.remove(arquivo)
            delete_json.append(arquivo)
            print(f" Excluído: {arquivo}")
        except OSError as e:
            print(f"Erro ao excluir {arquivo}: {e}")
    print(f"\nTotal de {len(delete_json)} arquivos .json excluídos!")
    return len(delete_json)

def choice_delete_json():
    delete_json = input("Deseja excluir todos os JSON's? : Y/N? ")
    if delete_json == "Y":
        clean_all_jsons()
    else:
        pass

# choice_delete_json()    