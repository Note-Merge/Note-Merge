const Screen = () => {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-white p-6">
        <h1 className="text-5xl font-extrabold text-black mb-4 shadow-lg">Merge Your Notes</h1>
        <p className="text-lg text-black mb-8">Combine multiple notes into a single, coherent document.</p>
        <div className="bg-zinc-100 rounded-lg shadow-2xl p-8 w-full max-w-lg">
          <label className="text-black mb-2" htmlFor="model-select">Select Model</label>
          <select id="model-select" className="block w-full p-3 rounded-md bg-zinc-200 text-black border border-zinc-400 shadow-md hover:shadow-lg transition duration-200">
            <option value="lstm">LSTM</option>
            <option value="transformer">Transformer</option>
          </select>
          <div className="my-6">
            <label className="text-black mb-2">Drag and drop files here</label>
            <div className="border-dashed border-2 border-zinc-400 rounded-lg p-6 text-center bg-zinc-50 hover:bg-zinc-200 transition duration-200">
              <p className="text-zinc-600">Or click to select files</p>
              <button className="mt-2 bg-zinc-300 text-black hover:bg-zinc-400 p-3 rounded-lg transition duration-200">Select Files</button>
            </div>
          </div>
          <label className="text-black mb-2" htmlFor="additional-notes">Additional Notes</label>
          <textarea id="additional-notes" rows="4" className="block w-full p-3 rounded-md bg-zinc-200 text-black border border-zinc-400 shadow-md hover:shadow-lg transition duration-200" placeholder="Add any additional notes or context here"></textarea>
          <button className="mt-6 bg-zinc-600 text-white hover:bg-zinc-700 p-3 rounded-lg w-full transition duration-200">Merge Notes</button>
        </div>
        <div className="mt-8 w-full max-w-lg bg-zinc-100 rounded-lg shadow-2xl p-4">
          <h2 className="text-lg font-bold text-black">Result</h2>
          <p className="text-zinc-600">Loading...</p>
          <button className="mt-2 bg-zinc-400 text-black hover:bg-zinc-500 p-3 rounded-lg transition duration-200">Copy to Clipboard</button>
        </div>
      </div>
    );
  };
  
  export default Screen;
  