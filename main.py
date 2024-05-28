import mysql.connector
import streamlit as st

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Lucca03",
    database="projetobd"
)
mycursor = mydb.cursor()

print("Connection Established")

try:
    mycursor.execute("""
        CREATE TRIGGER after_update_roteiro_pesquisa
        AFTER UPDATE ON Pesquisa
        FOR EACH ROW
        BEGIN
            IF OLD.roteiro != NEW.roteiro THEN
                INSERT INTO Log_Alteracao_Roteiro_Pesquisa (id_pesquisa, roteiro_antigo, roteiro_novo, data_alteracao)
                VALUES (OLD.id_pesquisa, OLD.roteiro, NEW.roteiro, NOW());
            END IF;
        END;
    """)
    mydb.commit()
    print("Trigger created successfully!")
except mysql.connector.Error as err:
    print("Error creating trigger:", err)

def main():
    relatorio_funcionario() 
    st.sidebar.title("Menu")
    page = st.sidebar.selectbox("Selecione a Pagina", ["Entrevista", "Administrador"])
    
    if page == "Entrevista":
        entrevista_page()
    elif page == "Administrador":
        administrador_page()

def entrevista_page():
    st.title("Empresa de Pesquisas - Entrevista")
    st.subheader("Pagina de Entrevista")
    tabs = ["Gerenciar Dados", "Buscar Entrevistas"]  
    tab = st.selectbox("Selecione uma Funcao", tabs)

    if tab == "Gerenciar Dados":
        manage_dados()
    elif tab == "Buscar Entrevistas":  
        buscar_entrevistas()  

def administrador_page():
    st.title("Empresa de Pesquisas - Administrador")
    st.subheader("Pagina do Administrador")
    tabs = ["Gerenciar Entrevistadores", "Gerenciar Entrevistados", "Gerenciar Pesquisas", "Gerenciar Clientes", "Gerenciar Perguntas", "Relatorio"]
    tab = st.selectbox("Selecione uma Funcao", tabs)

    if tab == "Gerenciar Entrevistadores":
        manage_entrevistadores()
    elif tab == "Gerenciar Entrevistados":
        manage_entrevistados()
    elif tab == "Gerenciar Pesquisas":
        manage_pesquisas()
    elif tab == "Gerenciar Clientes":
        manage_clientes()
    elif tab == "Gerenciar Perguntas":
        manage_perguntas()
    elif tab == "Relatorio":
        relatorio_page()

def relatorio_page():
    st.subheader("Relatorio")
    st.write("Insira o ID do entrevistador para gerar o relatorio:")
    id_entrevistador = st.text_input("ID do Entrevistador")

    if st.button("Gerar Relatorio"):
        relatorio = relatorio_funcionario_mysql(id_entrevistador)
        if relatorio:
            st.write(relatorio)
        else:
            st.write("Nenhum dado encontrado para gerar o relatorio.")

def relatorio_funcionario_mysql(id_entrevistador):
    try:
        mycursor.callproc("relatorio_funcionario")
        for result in mycursor.stored_results():
            relatorio = result.fetchall()
        return relatorio
    except mysql.connector.Error as err:
        print("Erro ao gerar o relatorio:", err)
        return None

def relatorio_funcionario():
    try:
        mycursor.execute("""
            CREATE FUNCTION relatorio_funcionario()
            RETURNS TEXT
            BEGIN
                DECLARE relatorio TEXT;
                SET relatorio = '';

                SELECT CONCAT('ID do Entrevistador: ', fk_entrevistador_id, ', Total de Dados Gerados: ', COUNT(*))
                INTO relatorio
                FROM Dados
                GROUP BY fk_entrevistador_id
                HAVING COUNT(*) > 0;

                IF relatorio IS NULL THEN
                    SET relatorio = 'Nenhum dado encontrado para gerar o relatorio.';
                END IF;

                RETURN relatorio;
            END;
        """)
        mydb.commit()
        print("Function created successfully!")
    except mysql.connector.Error as err:
        print("Error creating function:", err)

def manage_entrevistadores():
    st.subheader("Gerenciar Entrevistadores")
    option = st.selectbox("Selecione uma operacao", ("Criar", "Ler", "Atualizar", "Apagar"))

    if option == "Criar":
        st.subheader("Adicionar um Entrevistador")
        id_entrevistador = st.text_input("ID do Entrevistador")
        if st.button("Adicionar"):
            sql = "INSERT INTO Entrevistador (id_entrevistador) VALUES (%s)"
            val = (id_entrevistador,)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Entrevistador Adicionado com Sucesso!")

    elif option == "Ler":
        st.subheader("Ver Entrevistadores")
        mycursor.execute("SELECT * FROM Entrevistador")
        result = mycursor.fetchall()
        for row in result:
            st.write(row)

    elif option == "Atualizar":
        st.subheader("Atualizar Entrevistador")
        old_id = st.text_input("ID Antigo do Entrevistador")
        new_id = st.text_input("Novo ID do Entrevistador")
        if st.button("Atualizar"):
            sql = "UPDATE Entrevistador SET id_entrevistador=%s WHERE id_entrevistador=%s"
            val = (new_id, old_id)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Entrevistador Atualizado com Sucesso!")

    elif option == "Apagar":
        st.subheader("Apagar Entrevistador")
        id_entrevistador = st.text_input("ID do Entrevistador")
        if st.button("Apagar"):
            sql = "DELETE FROM Entrevistador WHERE id_entrevistador=%s"
            val = (id_entrevistador,)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Entrevistador Apagado com Sucesso!")

def manage_entrevistados():
    st.subheader("Gerenciar Entrevistados")
    option = st.selectbox("Selecione uma operacao", ("Criar", "Ler", "Atualizar", "Apagar"))

    if option == "Criar":
        st.subheader("Adicionar um Entrevistado")
        id_entrevistado = st.text_input("ID do Entrevistado")
        nome = st.text_input("Nome")
        idade = st.number_input("Idade", min_value=0)
        genero = st.text_input("Genero")
        religiao = st.text_input("Religiao")
        estado = st.text_input("Estado")
        profissao = st.text_input("Profissao")
        telefone = st.text_input("Telefone")
        rua = st.text_input("Rua")
        bairro = st.text_input("Bairro")
        fk_entrevistador_id = st.text_input("ID do Entrevistador")
        if st.button("Adicionar"):
            sql = """INSERT INTO Entrevistado 
                     (id_entrevistado, nome, idade, genero, religiao, estado, profissao, telefone, rua, bairro, fk_entrevistador_id) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            val = (id_entrevistado, nome, idade, genero, religiao, estado, profissao, telefone, rua, bairro, fk_entrevistador_id)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Entrevistado Adicionado com Sucesso!")

    elif option == "Ler":
        st.subheader("Ver Entrevistados")
        mycursor.execute("SELECT * FROM Entrevistado")
        result = mycursor.fetchall()
        for row in result:
            st.write(row)

    elif option == "Atualizar":
        st.subheader("Atualizar Entrevistado")
        id_entrevistado = st.text_input("ID do Entrevistado")
        campo = st.selectbox("Campo para Atualizar", ["nome", "idade", "genero", "religiao", "estado", "profissao", "telefone", "rua", "bairro", "fk_entrevistador_id"])
        novo_valor = st.text_input(f"Novo Valor para {campo}")
        if st.button("Atualizar"):
            sql = f"UPDATE Entrevistado SET {campo}=%s WHERE id_entrevistado=%s"
            val = (novo_valor, id_entrevistado)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Entrevistado Atualizado com Sucesso!")

    elif option == "Apagar":
        st.subheader("Apagar Entrevistado")
        id_entrevistado = st.text_input("ID do Entrevistado")
        if st.button("Apagar"):
            sql = "DELETE FROM Entrevistado WHERE id_entrevistado=%s"
            val = (id_entrevistado,)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Entrevistado Apagado com Sucesso!")

def buscar_entrevistas():
    st.subheader("Buscar Entrevistas")
    id_entrevistador = st.text_input("ID do Entrevistador")
    estado = st.text_input("Estado")

    if st.button("Buscar"):
        try:
            mycursor.execute("""
                CREATE OR REPLACE VIEW Lista_Entrevistados_Filtrada AS
                SELECT 
                    id_entrevistado,
                    nome,
                    idade,
                    genero,
                    religiao,
                    estado,
                    profissao,
                    telefone,
                    rua,
                    bairro,
                    fk_entrevistador_id
                FROM
                    Entrevistado
                WHERE
                    estado = %s AND fk_entrevistador_id = %s
            """, (estado, id_entrevistador))
            mydb.commit()
            
            mycursor.execute("SELECT * FROM Lista_Entrevistados_Filtrada")
            result = mycursor.fetchall()
            
            if result:
                st.title(f"Lista para entrevista do {estado} - Entrevistador {id_entrevistador}")
                for row in result:
                    st.write(row)
            else:
                st.write("Nenhum entrevistado encontrado para os criterios selecionados.")
        except mysql.connector.Error as err:
            st.error(f"Erro ao buscar entrevistas: {err}")

def manage_dados():
    st.subheader("Gerenciar Dados")
    option = st.selectbox("Selecione uma operacao", ("Criar", "Ler", "Atualizar", "Apagar"))

    if option == "Criar":
        st.subheader("Adicionar Dados")
        id_dados = st.text_input("ID dos Dados")
        r1 = st.text_input("Resposta 1")
        r2 = st.text_input("Resposta 2")
        r3 = st.text_input("Resposta 3")
        r4 = st.text_input("Resposta 4")
        r5 = st.text_input("Resposta 5")
        fk_entrevistado_id = st.text_input("ID do Entrevistado")
        fk_entrevistador_id = st.text_input("ID do Entrevistador")
        fk_pesquisa_id = st.text_input("ID da Pesquisa")
        if st.button("Adicionar"):
            sql = """INSERT INTO Dados 
                     (id_dados, r1, r2, r3, r4, r5, fk_entrevistado_id, fk_entrevistador_id, fk_pesquisa_id) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            val = (id_dados, r1, r2, r3, r4, r5, fk_entrevistado_id, fk_entrevistador_id, fk_pesquisa_id)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Dados Adicionados com Sucesso!")

    elif option == "Ler":
        st.subheader("Ver Dados")
        mycursor.execute("SELECT * FROM Dados")
        result = mycursor.fetchall()
        for row in result:
            st.write(row)

    elif option == "Atualizar":
        st.subheader("Atualizar Dados")
        id_dados = st.text_input("ID dos Dados")
        campo = st.selectbox("Campo para Atualizar", ["r1", "r2", "r3", "r4", "r5", "fk_entrevistado_id", "fk_entrevistador_id", "fk_pesquisa_id"])
        novo_valor = st.text_input(f"Novo Valor para {campo}")
        if st.button("Atualizar"):
            sql = f"UPDATE Dados SET {campo}=%s WHERE id_dados=%s"
            val = (novo_valor, id_dados)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Dados Atualizados com Sucesso!")

    elif option == "Apagar":
        st.subheader("Apagar Dados")
        id_dados = st.text_input("ID dos Dados")
        if st.button("Apagar"):
            sql = "DELETE FROM Dados WHERE id_dados=%s"
            val = (id_dados,)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Dados Apagados com Sucesso!")

def visualizar_mudancas_pesquisas():
    st.subheader("Mudancas nas Pesquisas")
    try:
        mycursor.execute("SELECT id_log, id_pesquisa, roteiro_antigo, roteiro_novo, DATE_FORMAT(data_alteracao, '%d/%m/%Y %H:%i:%s') AS data_alteracao FROM Log_Alteracao_Roteiro_Pesquisa")
        result = mycursor.fetchall()
        for row in result:
            st.write(row)
    except mysql.connector.Error as err:
        st.error(f"Erro ao recuperar os dados da tabela: {err}")

def manage_pesquisas():
    st.subheader("Gerenciar Pesquisas")
    option = st.selectbox("Selecione uma operacao", ("Criar", "Ler", "Atualizar", "Apagar", "Mudancas nas Pesquisas"))

    if option == "Criar":
        st.subheader("Adicionar uma Pesquisa")
        id_pesquisa = st.text_input("ID da Pesquisa")
        roteiro = st.text_input("Roteiro")
        estado = st.text_input("Estado")
        fk_cliente_id = st.text_input("ID do Cliente")
        if st.button("Adicionar"):
            sql = """INSERT INTO Pesquisa 
                     (id_pesquisa, roteiro, estado, fk_cliente_id) 
                     VALUES (%s, %s, %s, %s)"""
            val = (id_pesquisa, roteiro, estado, fk_cliente_id)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Pesquisa Adicionada com Sucesso!")

    elif option == "Ler":
        st.subheader("Ver Pesquisas")
        mycursor.execute("SELECT * FROM Pesquisa")
        result = mycursor.fetchall()
        for row in result:
            st.write(row)

    elif option == "Atualizar":
        st.subheader("Atualizar Pesquisa")
        id_pesquisa = st.text_input("ID da Pesquisa")
        campo = st.selectbox("Campo para Atualizar", ["roteiro", "estado", "fk_cliente_id"])
        novo_valor = st.text_input(f"Novo Valor para {campo}")
        if st.button("Atualizar"):
            sql = f"UPDATE Pesquisa SET {campo}=%s WHERE id_pesquisa=%s"
            val = (novo_valor, id_pesquisa)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Pesquisa Atualizada com Sucesso!")

    elif option == "Apagar":
        st.subheader("Apagar Pesquisa")
        id_pesquisa = st.text_input("ID da Pesquisa")
        if st.button("Apagar"):
            sql = "DELETE FROM Pesquisa WHERE id_pesquisa=%s"
            val = (id_pesquisa,)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Pesquisa Apagada com Sucesso!")

    elif option == "Mudancas nas Pesquisas":
        visualizar_mudancas_pesquisas()

def manage_clientes():
    st.subheader("Gerenciar Clientes")
    option = st.selectbox("Selecione uma operacao", ("Criar", "Ler", "Atualizar", "Apagar"))

    if option == "Criar":
        st.subheader("Adicionar um Cliente")
        id_cliente = st.text_input("ID do Cliente")
        estado = st.text_input("Estado")
        if st.button("Adicionar"):
            sql = """INSERT INTO Cliente 
                     (id_cliente, estado) 
                     VALUES (%s, %s)"""
            val = (id_cliente, estado)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Cliente Adicionado com Sucesso!")

    elif option == "Ler":
        st.subheader("Ver Clientes")
        mycursor.execute("SELECT * FROM Cliente")
        result = mycursor.fetchall()
        for row in result:
            st.write(row)

    elif option == "Atualizar":
        st.subheader("Atualizar Cliente")
        id_cliente = st.text_input("ID do Cliente")
        campo = st.selectbox("Campo para Atualizar", ["estado"])
        novo_valor = st.text_input(f"Novo Valor para {campo}")
        if st.button("Atualizar"):
            sql = f"UPDATE Cliente SET {campo}=%s WHERE id_cliente=%s"
            val = (novo_valor, id_cliente)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Cliente Atualizado com Sucesso!")

    elif option == "Apagar":
        st.subheader("Apagar Cliente")
        id_cliente = st.text_input("ID do Cliente")
        if st.button("Apagar"):
            sql = "DELETE FROM Cliente WHERE id_cliente=%s"
            val = (id_cliente,)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Cliente Apagado com Sucesso!")

def manage_perguntas():
    st.subheader("Gerenciar Perguntas")
    option = st.selectbox("Selecione uma operacao", ("Criar", "Ler", "Atualizar", "Apagar"))

    if option == "Criar":
        st.subheader("Adicionar Perguntas")
        id_pesquisa = st.text_input("ID da Pesquisa")
        p1 = st.text_input("Pergunta 1")
        p2 = st.text_input("Pergunta 2")
        p3 = st.text_input("Pergunta 3")
        p4 = st.text_input("Pergunta 4")
        p5 = st.text_input("Pergunta 5")
        if st.button("Adicionar"):
            sql = """INSERT INTO Realiza 
                     (id_pesquisa, p1, p2, p3, p4, p5) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            val = (id_pesquisa, p1, p2, p3, p4, p5)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Perguntas Adicionadas com Sucesso!")

    elif option == "Ler":
        st.subheader("Ver Perguntas")
        mycursor.execute("SELECT * FROM Realiza")
        result = mycursor.fetchall()
        for row in result:
            st.write(row)

    elif option == "Atualizar":
        st.subheader("Atualizar Perguntas")
        id_pesquisa = st.text_input("ID da Pesquisa")
        campo = st.selectbox("Campo para Atualizar", ["p1", "p2", "p3", "p4", "p5"])
        novo_valor = st.text_input(f"Novo Valor para {campo}")
        if st.button("Atualizar"):
            sql = f"UPDATE Realiza SET {campo}=%s WHERE id_pesquisa=%s"
            val = (novo_valor, id_pesquisa)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Pergunta Atualizada com Sucesso!")

    elif option == "Apagar":
        st.subheader("Apagar Perguntas")
        id_pesquisa = st.text_input("ID da Pesquisa")
        if st.button("Apagar"):
            sql = "DELETE FROM Realiza WHERE id_pesquisa=%s"
            val = (id_pesquisa,)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Perguntas Apagadas com Sucesso!")

if __name__ == "__main__":
    relatorio_funcionario()
    main()