import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class DashboardJSON:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard Inteligente")
        self.root.geometry("1700x900")

        # Variáveis
        self.df = None
        self.canvas = None
        self.fig = None
        self.arquivos_carregados = []

        # Criar interface
        self.create_widgets()

    # ===================== INTERFACE =====================
    def create_widgets(self):
        frame_botoes = tk.Frame(self.root, pady=5)
        frame_botoes.pack(fill=tk.X)

        botoes_info = [
            ("📂 Carregar JSON(s)", self.carregar_json),
            ("📊 Gerar Gráfico", self.gerar_grafico),
            ("📄 Exportar PDF", self.exportar_pdf),
            ("📈 Mais Análises", self.mais_analises),
            ("🧹 Limpar Tela", self.limpar_tela),
            ("❌ Fechar", self.fechar_app)
        ]
        for txt, cmd in botoes_info:
            tk.Button(frame_botoes, text=txt, width=18, command=cmd).pack(side=tk.LEFT, padx=3)

        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # Painel de controles
        frame_controles = tk.LabelFrame(main_pane, text="Configurações / Filtros", width=350, padx=10, pady=10)
        main_pane.add(frame_controles)

        tk.Label(frame_controles, text="Arquivos Carregados").pack()
        self.lb_arquivos = tk.Listbox(frame_controles, height=5)
        self.lb_arquivos.pack(fill=tk.X)
        tk.Button(frame_controles, text="Remover Arquivo Selecionado", command=self.remover_arquivo).pack(pady=2)

        tk.Label(frame_controles, text="Eixo X").pack(pady=(10,0))
        self.combo_x = ttk.Combobox(frame_controles, state="readonly", width=30)
        self.combo_x.pack()

        tk.Label(frame_controles, text="Eixo Y (múltiplos)").pack(pady=(10,0))
        self.listbox_y = tk.Listbox(frame_controles, selectmode=tk.MULTIPLE, exportselection=0, height=6)
        self.listbox_y.pack(fill=tk.X)

        tk.Label(frame_controles, text="Tipo de Gráfico").pack(pady=(10,0))
        self.tipo_grafico = ttk.Combobox(frame_controles, 
                                         values=["Barra","Linha","Pizza","Histograma","Boxplot"], 
                                         state="readonly", width=30)
        self.tipo_grafico.current(0)
        self.tipo_grafico.pack()

        # Filtros
        self.filtros = {}
        for col in ["UF","MUNICIPIO","","COMBUSTIVEL","COR"]:
            tk.Label(frame_controles, text=col).pack()
            lb = tk.Listbox(frame_controles, selectmode=tk.MULTIPLE, exportselection=0, height=5)
            scrollbar = tk.Scrollbar(frame_controles, orient=tk.VERTICAL, command=lb.yview)
            lb.config(yscrollcommand=scrollbar.set)
            lb.pack(fill=tk.X)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.filtros[col] = lb

        # Painel direito
        right_pane = tk.PanedWindow(main_pane, orient=tk.VERTICAL)
        main_pane.add(right_pane)

        # Insights
        frame_insights = tk.LabelFrame(right_pane, text="Insights", height=200)
        right_pane.add(frame_insights)
        self.txt_insights = tk.Text(frame_insights, height=10)
        self.txt_insights.pack(fill=tk.BOTH, expand=True)

        # Gráfico
        self.frame_grafico = tk.LabelFrame(right_pane, text="Gráfico", height=400)
        right_pane.add(self.frame_grafico)

        # Tabela
        frame_tabela = tk.LabelFrame(right_pane, text="Tabela de Dados", height=300)
        right_pane.add(frame_tabela)
        self.tabela = ttk.Treeview(frame_tabela)
        self.tabela.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar_table = tk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar_table.set)
        scrollbar_table.pack(side=tk.RIGHT, fill=tk.Y)

    # ===================== MÉTODOS =====================
    def carregar_json(self):
        arquivos = filedialog.askopenfilenames(filetypes=[("JSON", "*.json")])
        if not arquivos:
            return
        lista_dfs = []
        for arquivo in arquivos:
            try:
                df_temp = pd.read_json(arquivo)
                df_temp.fillna(0, inplace=True)
                lista_dfs.append(df_temp)
                self.arquivos_carregados.append(os.path.basename(arquivo))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar {arquivo}: {str(e)}")
                continue
        if lista_dfs:
            self.df = pd.concat(lista_dfs, ignore_index=True)
            self.configurar_combos()
            self.configurar_filtros()
            self.atualizar_tabela()
            self.atualizar_lista_arquivos()
            messagebox.showinfo("Sucesso", "Arquivos carregados com sucesso!")

    def atualizar_lista_arquivos(self):
        self.lb_arquivos.delete(0, tk.END)
        for arq in self.arquivos_carregados:
            self.lb_arquivos.insert(tk.END, arq)

    def remover_arquivo(self):
        selecao = self.lb_arquivos.curselection()
        if not selecao:
            return
        idx = selecao[0]
        self.arquivos_carregados.pop(idx)
        self.lb_arquivos.delete(idx)
        messagebox.showinfo("Removido", "Arquivo removido!")
        self.df = None
        if self.arquivos_carregados:
            dfs = []
            for nome in self.arquivos_carregados:
                path = filedialog.askopenfilename(title=f"Selecione novamente {nome}", filetypes=[("JSON","*.json")])
                if path:
                    dfs.append(pd.read_json(path))
            if dfs:
                self.df = pd.concat(dfs, ignore_index=True)
                self.configurar_combos()
                self.configurar_filtros()
                self.atualizar_tabela()

    def configurar_combos(self):
        if self.df is None:
            return
        cols = list(self.df.columns)
        num = self.df.select_dtypes(include="number").columns.tolist()
        txt = self.df.select_dtypes(exclude="number").columns.tolist()
        self.combo_x["values"] = txt if txt else cols
        self.listbox_y.delete(0, tk.END)
        for c in num:
            self.listbox_y.insert(tk.END, c)
        if self.combo_x["values"]:
            self.combo_x.current(0)
        if self.listbox_y.size() > 0:
            self.listbox_y.selection_set(0)

    def configurar_filtros(self):
        if self.df is None:
            return
        for col, lb in self.filtros.items():
            lb.delete(0, tk.END)
            if col in self.df.columns:
                valores = sorted(self.df[col].dropna().unique())
                for val in valores:
                    lb.insert(tk.END, val)

    def atualizar_tabela(self):
        if self.df is None:
            return
        self.tabela.delete(*self.tabela.get_children())
        self.tabela["columns"] = list(self.df.columns)
        self.tabela["show"] = "headings"
        for col in self.df.columns:
            self.tabela.heading(col, text=col)
        for _, row in self.df.iterrows():
            self.tabela.insert("", tk.END, values=list(row))

    def limpar_tela(self):
        self.txt_insights.delete("1.0", tk.END)
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = None
        self.fig = None

    def fechar_app(self):
        self.root.destroy()

    # ===================== FILTROS =====================
    def aplicar_filtros(self, df):
        for col, lb in self.filtros.items():
            selecionados = [lb.get(i) for i in lb.curselection()]
            if selecionados:
                df = df[df[col].isin(selecionados)]
        return df

    # ===================== GRÁFICOS =====================
    def gerar_grafico(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Carregue pelo menos um JSON.")
            return

        x_col = self.combo_x.get()
        y_selecionados = [self.listbox_y.get(i) for i in self.listbox_y.curselection()]
        tipo = self.tipo_grafico.get()

        if not x_col or not y_selecionados:
            messagebox.showwarning("Aviso", "Selecione eixo X e pelo menos um eixo Y.")
            return

        df_filtrado = self.aplicar_filtros(self.df.copy())
        if df_filtrado.empty:
            messagebox.showwarning("Aviso", "Nenhum dado após aplicar filtros.")
            return

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        n = len(y_selecionados)
        fig, axs = plt.subplots(n, 1, figsize=(12, 4*n))
        if n == 1:
            axs = [axs]

        for ax, y_col in zip(axs, y_selecionados):
            try:
                dados = df_filtrado.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(10)
            except:
                dados = df_filtrado[x_col].value_counts().head(10)

            if tipo == "Barra":
                dados.plot(kind="bar", ax=ax)
            elif tipo == "Linha":
                dados.plot(kind="line", marker="o", ax=ax)
            elif tipo == "Pizza":
                dados.plot(kind="pie", autopct='%1.1f%%', ax=ax)
            elif tipo == "Histograma":
                df_filtrado[y_col].plot(kind="hist", bins=20, ax=ax)
            elif tipo == "Boxplot":
                df_filtrado[y_col].plot(kind="box", ax=ax)

            ax.set_title(f"{y_col} por {x_col}")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            plt.setp(ax.get_xticklabels(), rotation=45)

        plt.tight_layout()
        self.fig = fig
        self.canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.gerar_relatorio(df_filtrado, x_col, y_selecionados)

    # ===================== RELATÓRIO DIDÁTICO =====================
    def gerar_relatorio(self, df, x_col, y_cols):
        texto = "📊 RELATÓRIO EXPLICADO (FÁCIL DE ENTENDER)\n\n"

        for y_col in y_cols:
            if y_col not in df.columns:
                continue

            total = df[y_col].sum()
            media = df[y_col].mean()
            maximo = df[y_col].max()
            minimo = df[y_col].min()

            texto += f"🔎 O que estamos analisando?\n"
            texto += f"→ A coluna '{y_col}' em relação a '{x_col}'.\n\n"

            texto += f"📌 Resumo geral:\n"
            texto += f"- Soma total: {total:,.2f}\n"
            texto += f"- Média: {media:,.2f}\n"
            texto += f"- Maior valor encontrado: {maximo:,.2f}\n"
            texto += f"- Menor valor encontrado: {minimo:,.2f}\n\n"

            grupo = df.groupby(x_col)[y_col].sum().sort_values(ascending=False)
            if not grupo.empty:
                maior = grupo.idxmax()
                menor = grupo.idxmin()

                texto += f"📍 Onde acontece mais?\n"
                texto += f"- O maior valor está em '{maior}' com {grupo.max():,.2f}\n"

                texto += f"\n📍 Onde acontece menos?\n"
                texto += f"- O menor valor está em '{menor}' com {grupo.min():,.2f}\n\n"

                texto += "🏆 Top 3 (quem mais aparece):\n"
                for i, (idx, val) in enumerate(grupo.head(3).items(), 1):
                    texto += f"{i}º lugar: {idx} → {val:,.2f}\n"

            # 🧠 EXPLICAÇÃO HUMANA
            texto += "\n💡 O que isso significa na prática?\n"
            if media > (total / len(df)):
                texto += "- Existem valores altos que puxam a média para cima.\n"
            else:
                texto += "- Os valores estão bem distribuídos, sem grandes picos.\n"
            if maximo > media * 2:
                texto += "- Existe um valor muito alto comparado aos outros (pico).\n"
            texto += "- Isso ajuda a entender onde estão os maiores impactos nos dados.\n"
            texto += "\n" + "="*60 + "\n\n"

        self.txt_insights.delete("1.0", tk.END)
        self.txt_insights.insert(tk.END, texto)

    # ===================== MAIS ANÁLISES DIDÁTICAS =====================
    def mais_analises(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Carregue algum JSON primeiro!")
            return

        df = self.aplicar_filtros(self.df.copy())
        if df.empty:
            messagebox.showwarning("Aviso", "Nenhum dado após filtros!")
            return

        texto = "\n📈 ANÁLISES EXPLICADAS (SEM TERMOS TÉCNICOS)\n\n"

        num_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(exclude="number").columns.tolist()

        # Números
        if num_cols:
            texto += "🔢 Sobre os números:\n\n"
            for col in num_cols:
                media = df[col].mean()
                minimo = df[col].min()
                maximo = df[col].max()
                texto += f"🔹 {col}\n"
                texto += f"- Em média: {media:,.2f}\n"
                texto += f"- Vai de {minimo:,.2f} até {maximo:,.2f}\n"
                if maximo > media * 2:
                    texto += "- Existe um valor muito alto comparado aos outros.\n"
                else:
                    texto += "- Os valores são relativamente próximos.\n"
                texto += "\n"

        # Categorias
        if cat_cols:
            texto += "\n🏷️ Sobre os tipos/categorias:\n\n"
            for col in cat_cols:
                texto += f"🔹 {col}\n"
                top = df[col].value_counts().head(3)
                texto += "Mais comuns:\n"
                for val, count in top.items():
                    texto += f"- {val} aparece {count} vezes\n"
                texto += "👉 Isso mostra quais opções dominam nos dados.\n\n"

        # Resumo
        texto += "\n🧠 RESUMO GERAL (em linguagem simples):\n\n"
        if "UF" in df.columns:
            top_uf = df["UF"].value_counts().idxmax()
            texto += f"- O estado que mais aparece é: {top_uf}\n"
        if "COMBUSTIVEL" in df.columns:
            top_comb = df["COMBUSTIVEL"].value_counts().idxmax()
            texto += f"- O combustível mais comum é: {top_comb}\n"
        if "ANO" in df.columns:
            texto += f"- Os dados vão de {df['ANO'].min()} até {df['ANO'].max()}\n"

        texto += "\n👉 Em resumo: esses dados mostram padrões claros de onde estão as maiores concentrações.\n"

        self.txt_insights.insert(tk.END, texto)

    # ===================== EXPORTAR PDF =====================
    def exportar_pdf(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Não há dados para exportar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not file_path:
            return

        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Relatório Completo - Dashboard Inteligente")
        c.setFont("Helvetica", 10)
        y = height - 70
        c.drawString(50, y, "Arquivos carregados: " + ", ".join(self.arquivos_carregados))
        y -= 40

        # Insights
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Insights e Análises")
        y -= 25
        c.setFont("Helvetica", 9)

        texto = self.txt_insights.get("1.0", tk.END).split("\n")
        for linha in texto:
            if linha.strip() == "":
                y -= 5
                continue
            c.drawString(50, y, linha[:90])
            y -= 12
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 9)

        # Gráficos
        if self.fig:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp.close()
            self.fig.savefig(tmp.name, bbox_inches='tight', dpi=150)

            c.showPage()
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 50, "Gráfico(s) Gerado(s)")
            y = height - 80
            c.drawImage(tmp.name, 50, y - 400, width=500, height=400)
            os.unlink(tmp.name)

        c.save()
        messagebox.showinfo("Sucesso", f"PDF salvo em: {file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardJSON(root)
    root.mainloop()