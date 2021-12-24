import React from "react";
import "./App.css";
import logo from "./assets/images/ryuina.jpg";

async function SendImageAPI(url: string, imageFormData: FormData) {
  if (url === undefined) {
    console.log("[ERROR]Url is empty.");
    return Response.error();
  }

  return await fetch(url, {
    method: "POST",
    body: imageFormData,
  });
}

const App = () => {
  const onFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files == null) {
      return;
    }

    console.log(e.target.files);
    if (e.target.files.length <= 0) {
      return;
    }

    const formData = new FormData();
    formData.append("file", e.target.files[0]);
    const response = SendImageAPI("http://127.0.0.1:5000/api", formData)
      .then((result) => {
        console.log(result.status);
        result.json().then((result) => {
          console.log(result);
        });
      })
      .catch((result) => {
        console.log(result);
      });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Scenery Tagging Service(Demo)</h1>
        <img src={logo} className="App-logo" alt="logo" />
        <label htmlFor="upload-image">Select a scenery photo(JPG/JPEG only)</label>
        <input type="file" id="upload-image" accept=".jpg, .jepg" onChange={onFileInputChange} />
      </header>
    </div>
  );
};

export default App;
