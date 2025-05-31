import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import seaborn as sns
sns.set_context('notebook')
import pdb

df = pd.read_csv('./format_builder/format_builder.csv')
types = ['Normal','Fire','Water','Grass','Electric','Ice',
         'Poison','Flying','Fighting','Rock','Ground','Bug',
         'Psychic','Dark','Ghost','Dragon','Steel','Fairy']

# Create the main window
root = tk.Tk()
root.title("Format Builder")
root.geometry("600x600")

def on_closing():
    print("Tkinter window closed. Exiting script.")
    root.quit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Create a Notebook (tab control)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Create Tab 1 with 5 checkboxes and an input text box
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='Format rules')

checkbox_vars1 = []
allowances = ['Allow Restricteds?','Allow Mythicals?','Require Fake Out?',
              'Require Trick Room?','Require Intimidate?']
for i in range(5):
    if i > 1:
        var = tk.BooleanVar(value=True)
    else:
        var = tk.BooleanVar()
    cb = tk.Checkbutton(tab1, text=f"{allowances[i]}", variable=var)
    cb.grid(row=i, column=0, sticky="w", padx=10, pady=5)
    checkbox_vars1.append(var)

# Input Text Box
label = tk.Label(tab1, text="Number of Pokemon:")
label.grid(row=6, column=0, padx=10, pady=(20, 5), sticky="w")
entry = tk.Entry(tab1, width=30)
entry.insert(tk.END, "24")
entry.grid(row=7, column=0, padx=10, pady=5)
status = tk.Label(tab1, text="Ready to generate", wraplength=300, justify='left')
status.grid(row=9, column=0, padx=10, pady=(20, 5), sticky="w")

# Function to run when button is clicked
def on_submit(df, types):
    
    try:
        n_pokemon = int(entry.get())
    except:
        status.config(text='Enter an integer number of Pokemon')
        return
    if n_pokemon < 6:
        status.config(text='You need at least 6 Pokemon')
        return

    tab1_vars = [x.get() for x in checkbox_vars1]
    tab2_vars = [x.get() for x in checkbox_vars2]
    if n_pokemon < np.sum(tab2_vars):
        status.config(text='You have fewer Pokemon than required types')
        return
    
    req_types = np.array(types)[tab2_vars]
    
    picks = []
    if tab1_vars[0] == False:
        df = df[df['Restricted'] == 0]
    if tab1_vars[1] == False:
        df = df[df['Mythical'] == 0]
    if tab1_vars[2] == True:
        picks.append(df[(df['Fake Out'] == 1) & (~df['Pokemon'].isin(picks))]['Pokemon'].sample(n=1).iloc[0])
    if tab1_vars[3] == True:
        picks.append(df[(df['Trick Room'] == 1) & (~df['Pokemon'].isin(picks))]['Pokemon'].sample(n=1).iloc[0])
    if tab1_vars[4] == True:
        picks.append(df[(df['Intimidate'] == 1) & (~df['Pokemon'].isin(picks))]['Pokemon'].sample(n=1).iloc[0])

    typings = df[df['Pokemon'].isin(picks)]['Typing'].to_list()
    typings = '/'.join(typings)

    current_types = [t.lower() for t in types if t.lower() in typings]
    for t in req_types:
        if t.lower() not in current_types:
            type_pick = df[(df['Typing'].str.contains(t.lower())) & (~df['Pokemon'].isin(picks))]['Pokemon'].sample(1).iloc[0]
            picks.append(type_pick)

            typings = df[df['Pokemon'] == type_pick]['Typing'].to_list()
            typings = '/'.join(typings)
            added_types = [ty.lower() for ty in types if ty.lower() in typings and ty.lower() not in current_types]
            for ty in added_types:
                current_types.append(ty)

    remaining_picks = n_pokemon - len(picks)
    final_picks = df[~df['Pokemon'].isin(picks)]['Pokemon'].sample(remaining_picks).to_list()
    for pick in final_picks:
        picks.append(pick)

    output_str = ', '.join(picks)
    status.config(text=f'Your {n_pokemon} are: {output_str}')

    sns.set_context('notebook')

    df_picks = df[df['Pokemon'].isin(picks)]
    bst = df_picks[['HP','Attack','Defense','Sp.Atk','Sp.Def','Speed']].sum(axis=1).to_list()
    df_picks = df_picks.assign(BST=bst)
    stats_df = pd.DataFrame()
    stats_df['Stats'] = ['','','Top 3','','','Average','','','Bottom 3','','']
    for stat in ['HP','Attack','Defense','Sp.Atk','Sp.Def','Speed','BST']:
        best_mon = df_picks.loc[df_picks[stat].idxmax(), 'Pokemon']
        top3 = df_picks.sort_values(stat, ascending=False).head(3)[stat].to_list()
        avg = np.round(df_picks[stat].mean(),1)
        bot3 = df_picks.sort_values(stat, ascending=False).tail(3)[stat].to_list()
        worst_mon = df_picks.loc[df_picks[stat].idxmin(), 'Pokemon']
        col = [best_mon,top3[0],top3[1],top3[2],'',avg,'',bot3[0],bot3[1],bot3[2],worst_mon]
        stats_df[stat] = col

    df_temp = df_picks.drop_duplicates(['Pokemon','Typing'])
    type_dict = {}
    for t in types:
        type_dict[t] = df_temp[df_temp['Typing'].str.contains(t.lower())]['Pokemon'].to_list()

    fig, ax = plt.subplots(figsize=(8, 8))
    plt.rcParams.update({'font.size': 16})
    ax.axis('off')
    ax.table(cellText=stats_df, colWidths=[0.15]*8,
             loc='center', colLabels=None, cellLoc='center', rowLabels=None)
    
    canvas = FigureCanvasTkAgg(fig, master=tab3)  # A tk.DrawingArea
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    fig, ax = plt.subplots(figsize=(8,8))
    ax.axis('off')
    df_speed = df_picks[['Pokemon','Variant','Speed']].sort_values('Speed',ascending=False).fillna('')
    full_names = (df_speed['Pokemon']+' '+df_speed['Variant']).str.strip().to_list()
    df_speed = df_speed.assign(full_name=full_names)
    full_texts = (df_speed['full_name']+', '+df_speed['Speed'].astype(str)).to_list()
    df_speed = df_speed.assign(full_text=full_texts)
    spacing = 1/len(df_speed)
    i = 0
    for j, row in df_speed.iterrows():
        if i%2 == 0:
            ha = 'right'
        else:
            ha = 'left'
        ax.annotate(text=row['full_text'],xy=(0.45+0.1*(i%2),1-spacing*i),ha=ha, fontsize=12)
        i += 1
    
    minimum = df_speed['Speed'].min()
    scaling = df_speed['Speed'].max()-minimum
    ax.vlines(x=0.5,ymin=0,ymax=1,color='black')
    ax.scatter(x=[0.5]*len(df_speed),y=(df_speed['Speed']-minimum)/scaling,color='black')
    ax.set_xlim(0,1)

    canvas = FigureCanvasTkAgg(fig, master=tab4)  # A tk.DrawingArea
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    i = 0
    for t, mons in type_dict.items():
        mons_str = ', '.join(mons)
        label = tk.Label(tab5, text=f"{t}: {mons_str}")
        label.grid(row=i+1, column=0, padx=10, pady=(3, 5), sticky="w")
        i += 1

    # fig, ax = plt.subplots(figsize=(8,8), tight_layout=True)
    # df_plot = pd.melt(df_picks[['HP','Attack','Defense','Sp.Atk','Sp.Def','Speed']].reset_index(),
    #                   id_vars = 'index', var_name = 'stat', value_name = 'value')
    # sns.scatterplot(data = df_plot, x = 'stat', y = 'value', hue = 'stat', ax=ax)
    # i = 0
    # for key, value in best_stats.items():
    #     ax.annotate(xy=(i,1.1*value[1]),text=value[0],rotation = 45, ha='left', va='center')
    #     i += 1
    # i = 0
    # for key, value in worst_stats.items():
    #     ax.annotate(xy=(i,0.7*value[1]),text=value[0],rotation = -45, ha='left', va='center')
    #     i += 1
    # ax.set_xlabel('Stat')
    # ax.set_ylabel('Value')
    # ax.set_ylim(0,df_plot['value'].max()+40)
    # ax.get_legend().remove()

    # canvas = FigureCanvasTkAgg(fig, master=tab3) # root is your Tkinter window
    # canvas.draw()
    # canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    # toolbar = NavigationToolbar2Tk(canvas, tab3)
    # toolbar.update()
    # canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


# Add Submit Button
submit_button = tk.Button(tab1, text="Generate", command=lambda: on_submit(df, types))
submit_button.grid(row=8, column=0, padx=10, pady=20)

# Create Tab 2 with 18 checkboxes
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Required Types')

def toggle_all_tab2():
    current_state = all(var.get() for var in checkbox_vars2)
    new_state = not current_state
    for var in checkbox_vars2:
        var.set(new_state)
    toggle_button.config(text="Deselect All" if new_state else "Select All")

checkbox_vars2 = []

for i in range(18):
    var = tk.BooleanVar(value=True)
    cb = tk.Checkbutton(tab2, text=f"{types[i]}", variable=var)
    cb.grid(row=i//3, column=i%3, sticky="w", padx=10, pady=5)
    checkbox_vars2.append(var)

toggle_button = tk.Button(tab2, text="Deselect All", command=toggle_all_tab2)
toggle_button.grid(row=6, column=0, columnspan=3, pady=10)

tab3 = ttk.Frame(notebook)
notebook.add(tab3, text='Stat Distribution')

tab4 = ttk.Frame(notebook)
notebook.add(tab4, text='Speed tiers')

tab5 = ttk.Frame(notebook)
notebook.add(tab5, text='Type Counts')

# Run the GUI loop
root.mainloop()