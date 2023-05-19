from flask import Flask, render_template
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import scipy

app = Flask("Dashboard")

playstore = pd.read_csv("data/googleplaystore.csv")

playstore.drop_duplicates(subset = ["App"], keep= False) 

# bagian ini untuk menghapus row 10472 karena nilai data tersebut tidak tersimpan pada kolom yang benar
playstore.drop([10472], inplace=True)

most_categories = "FAMILY"
Total = "1832"
rev_table = playstore.groupby('App').agg({'Reviews':'sum'}).sort_values('Reviews', ascending=False).head(10)
playstore = playstore.astype({
    "Type": "category",
    "Category": "category",
    "App": "category",
    "Genres": "category"
})


playstore["Installs"] = playstore["Installs"].apply(lambda x: x.replace(",",""))
playstore["Installs"] = playstore["Installs"].apply(lambda x: x.replace("+", ""))

# Bagian ini untuk merapikan kolom Size, Anda tidak perlu mengubah apapun di bagian ini
playstore['Size'].replace('Varies with device', np.nan, inplace = True ) 
playstore.Size = (playstore.Size.replace(r'[kM]+$', '', regex=True).astype(float) * \
             playstore.Size.str.extract(r'[\d\.]+([kM]+)', expand=False)
            .fillna(1)
            .replace(['k','M'], [10**3, 10**6]).astype(int))
playstore['Size'].fillna(playstore.groupby('Category')['Size'].transform('mean'),inplace = True)

playstore["Price"] = playstore["Price"].apply(lambda x: x.replace("$",""))
playstore["Price"] = playstore["Price"].astype("float64")

# Ubah tipe data Reviews, Size, Installs ke dalam tipe data integer
playstore["Reviews"] = playstore["Reviews"].astype("int64"); playstore["Installs"] = playstore["Installs"].astype("int64"); playstore["Size"] = playstore["Size"].astype("int64")

@app.route("/")
# This fuction for rendering the table
def index():
    df2 = playstore.copy()

    # Statistik
    top_category = pd.crosstab(
    index = df2["Category"],
    columns = "top_category").sort_values(by = "top_category",ascending = False)

    # Dictionary stats digunakan untuk menyimpan beberapa data yang digunakan untuk menampilkan nilai di value box dan tabel
    stats = {
        'most_categories' : most_categories,
        'total': Total,
        'rev_table' : rev_table.to_html(classes=['table thead-light table-striped table-bordered table-hover table-sm'])
    }


    # bagian ini digunakan untuk mengconvert matplotlib png ke base64 agar dapat ditampilkan ke template html
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    # variabel result akan dimasukkan ke dalam parameter di fungsi render_template() agar dapat ditampilkan di 
    # halaman html
    result = str(figdata_png)[2:-1]
    
    cat_order = playstore.groupby("Reviews").agg({
    "Category" : "count"
     }).rename({'Category':'Total'}, axis=1).sort_values(by = "Reviews").head().plot(kind= "barh")
    X = "Total"
    Y = "Category"
    my_colors = ['r','g','b','k','y','m','c']


    # bagian ini digunakan untuk membuat bar plot
    plt.barh(Y, X, color=my_colors)

 
    # bagian ini digunakan untuk menyimpan plot dalam format image.png
    plt.savefig('cat_order.png',bbox_inches="tight")
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]

    ## Scatter Plot
    X = playstore["Reviews"].values # axis x
    Y = playstore["Rating"].values # axis y
    area = playstore["Installs"].values/10000000 # ukuran besar/kecilnya lingkaran scatter plot
    fig = plt.figure(figsize=(5,5))
    fig.add_subplot()
 
    # isi nama method untuk scatter plot, variabel x, dan variabel y
    plt.scatter(x=X,y=Y, s=area, alpha=0.3)
    plt.xlabel('Reviews')
    plt.ylabel('Rating')
    plt.savefig('rev_rat.png',bbox_inches="tight")

    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result2 = str(figdata_png)[2:-1]

    ## Histogram Size Distribution
    X=(playstore["Size"]/1000000).values
    fig = plt.figure(figsize=(5,5))
    fig.add_subplot()
    
    plt.hist(X,bins=100, density=True,  alpha=0.75)
    plt.xlabel('Size')
    plt.ylabel('Frequency')
    plt.savefig('hist_size.png',bbox_inches="tight")

    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result3 = str(figdata_png)[2:-1]

    ## Buatlah sebuah plot yang menampilkan insight di dalam data 
    X = playstore["Size"].values # axis x
    Y = playstore["Installs"].values # axis y

    fig, ax = plt.subplots(figsize=(8,5))

    ax.set_title("Density Plot of App Size")
    ax.set_xlabel("Size")
    ax.set_ylabel("Density")

    playstore["Size"].plot(kind="density", ax=ax)
    plt.savefig('Density_plot.png',bbox_inches="tight")  

    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result4 = str(figdata_png)[2:-1]

    # Tambahkan hasil result plot pada fungsi render_template()
    return render_template('index.html', stats=stats, result=result, result2=result2, result3=result3,result4=result4)

if __name__ == "__main__": 
    app.run(debug=True)
