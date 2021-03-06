import React, { useState } from "react";
import logo from "./assets/images/ryuina.jpg";

const ImageTagging = () => {
  const [isAfterPredict, setAfterPredict] = useState(false);
  const [enTags, setEnTags] = useState([]);
  const [jaTags, setJaTags] = useState([]);

  const SendImageAPI = async (url: string, imageFormData: FormData) => {
    setAfterPredict(false);
    if (url === undefined) {
      console.log("[ERROR]Url is empty.");
      return Response.error();
    }

    return await fetch(url, {
      method: "POST",
      body: imageFormData,
    });
  };

  const [uploadedImage, setUploadedImage] = useState(String);

  const onFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files == null) {
      return;
    }

    console.log(e.target.files);
    if (e.target.files.length <= 0) {
      return;
    }

    setUploadedImage(URL.createObjectURL(e.target.files[0]));

    const formData = new FormData();
    formData.append("file", e.target.files[0]);
    SendImageAPI("http://127.0.0.1:5000/api", formData)
      .then((response) => response.json())
      .then((response) => {
        console.log(response.predict_tags);
        setEnTags(response.predict_tags.English);
        setJaTags(response.predict_tags["日本語"]);
        setAfterPredict(true);
      })
      .catch((response) => {
        console.log(response);
        alert("Error");
      });
  };

  if (isAfterPredict) {
    return (
      <div className="ImageTagging">
        <header className="ImageTagging-header">
          <div>
            <img id="img-uploaded" src={uploadedImage} alt="uploaded" />
            <p>Tags: {enTags.join(", ")}</p>
            <p>タグ: {jaTags.join(", ")}</p>
          </div>
          <div id="upload-area">
            <label htmlFor="upload-image">Select a scenery photo(JPG/JPEG only)</label>
            <input type="file" id="upload-image" accept=".jpg, .jepg" onChange={onFileInputChange} />
          </div>
        </header>
      </div>
    );
  } else {
    return (
      <div className="ImageTagging">
        <header className="ImageTagging-header">
          <img src={logo} className="App-logo" alt="logo" />
          <div id="upload-area">
            <label htmlFor="upload-image">Select a scenery photo(JPG/JPEG only)</label>
            <input type="file" id="upload-image" accept=".jpg, .jepg" onChange={onFileInputChange} />
          </div>
        </header>
      </div>
    );
  }
};

export default ImageTagging;
