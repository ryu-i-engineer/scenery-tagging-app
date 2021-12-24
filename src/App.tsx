import "./App.css";
import logo from "./assets/images/ryuina.jpg";
import ImageTagging from "./ImageTagging";

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Scenery Tagging Service(Demo)</h1>
        <img src={logo} className="App-logo" alt="logo" />
        <ImageTagging />
      </header>
    </div>
  );
};

export default App;
