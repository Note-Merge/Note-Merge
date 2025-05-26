import Navbar from "../components/Navbar";
import FileUpload from "../components/FileUpload";
import Particles from "@/components/Particles/Particles";

export default function Home() {
  return (
    <>
    <div className="relative min-h-screen bg-neutral-900 overflow-hidden">
    <div className="absolute inset-0 z-0 pointer-events-none">
      <Particles/>
    </div>
    <Navbar/>
    <FileUpload/>
    </div>
    </>
  );
}
