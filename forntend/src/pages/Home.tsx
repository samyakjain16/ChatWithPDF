import PDFUpload from '/Users/mayankjain/Downloads/pdf-chat-app/forntend/src/components/pdf/PDFUploader.tsx';
import PDFList from '/Users/mayankjain/Downloads/pdf-chat-app/forntend/src/components/pdf/PDFList.tsx'

const Home = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-8">PDF Chat</h1>
      <div className="mb-8">
        <PDFUpload />
      </div>
      <PDFList />
    </div>
  );
};

export default Home;