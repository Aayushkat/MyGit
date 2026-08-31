#filename=main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
 
from App.Routers import Health_test          #importing Healht_test.py from path App/routers 
from App.Routers import github

app=FastAPI(title="Mygit")
#The 'router=APIrouter()' inside the the file hello.py
app.include_router(Health_test.router)
app.include_router(github.router)





#fastapi only returns JSON thats why we have a response class
## To return HTML instead, we can use FastAPI's HTMLResponse class.View
#https://fastapi.tiangolo.com/advanced/custom-response/

@app.get("/users",response_class=HTMLResponse)#to handle the get request sent by browser/curl/client accesing our server
def home():
    return """
<title>GitHub Profile Search</title>

<style>
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    body {
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;

        font-family: Arial, sans-serif;
        background: #0d1117;
        color: #f0f6fc;
    }

    .container {
        width: 90%;
        max-width: 500px;
        padding: 40px;

        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 16px;

        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    h1 {
        margin-bottom: 30px;
        font-size: 28px;
    }

    form {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }

    label {
        display: flex;
        flex-direction: column;
        gap: 8px;

        text-align: left;
        font-size: 14px;
        color: #8b949e;
    }

    input {
        width: 100%;
        padding: 12px 14px;

        font-size: 16px;
        color: #f0f6fc;
        background: #0d1117;

        border: 1px solid #30363d;
        border-radius: 8px;

        outline: none;
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    input:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.15);
    }

    button {
        padding: 12px;

        font-size: 16px;
        font-weight: 600;

        color: white;
        background: #238636;

        border: none;
        border-radius: 8px;

        cursor: pointer;
        transition: background 0.2s, transform 0.1s;
    }

    button:hover {
        background: #2ea043;
    }

    button:active {
        transform: scale(0.98);
    }
</style>

</head>

<body>

<div class="container">
    <h1>Search GitHub Profile</h1>

    <form
        method="post"
        onsubmit="this.action = '/users/' + document.querySelector('input[name=username]').value"
    >
        <label>
            GitHub Username
            <input
                type="text"
                name="username"
                placeholder="e.g. torvalds"
                required
            >
        </label>

        <button type="submit">
            Search Profile
        </button>
    </form>
</div>
    """

