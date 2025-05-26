import Navbar from "../components/Navbar";
import FileUpload from "../components/FileUpload";
import Particles from "@/components/Particles/Particles";
import TextBox from "@/components/TextBox";

export default function Home() {
  return (
    <>
      <div className="relative min-h-screen bg-neutral-900 overflow-hidden">
        <div className="absolute inset-0 z-0 pointer-events-none">
          <Particles />
        </div>
        <Navbar />
        <FileUpload />
        <TextBox />
        <div>
          <div className="flex flex-col mx-auto max-w-3xl mt-4 mb-4">
            <div className="relative group">
              <button className="relative inline-block p-px font-semibold leading-6 text-white bg-gray-800 shadow-2xl cursor-pointer rounded-xl shadow-zinc-900 transition-transform duration-300 ease-in-out hover:scale-105 active:scale-95">
                <span className="absolute inset-0 rounded-xl bg-gradient-to-r from-teal-400 via-blue-500 to-purple-500 p-[2px] opacity-0 transition-opacity duration-500 group-hover:opacity-100"></span>

                <span className="relative z-10 block px-3 py-3 rounded-xl bg-gray-950">
                  <div className="relative z-10 flex items-center space-x-2">
                    <span className="transition-all duration-500 group-hover:translate-x-1">
                      Merge Notes
                    </span>
                  </div>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
