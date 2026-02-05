import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import MetadataPanel from './components/MetadataPanel';
import ChatPanel from './components/ChatPanel';

function App() {
    const [retrievedChunks, setRetrievedChunks] = useState([]);

    const handleChunksRetrieved = (chunks) => {
        setRetrievedChunks(chunks);
    };

    const handleUploadSuccess = (result) => {
        console.log('Upload successful:', result);
    };

    return (
        <div className="min-h-screen p-3">
            {/* Header */}
            <header className="mb-3">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
                            RAG Application
                        </h1>
                        <p className="text-dark-400 text-sm mt-1">
                            Powered by <span className="text-primary-400 font-semibold">Endee</span> Vector Database
                        </p>
                    </div>

                    {/* Endee Badge */}
                    <div className="glass-panel px-4 py-2 flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-dark-300">Endee Connected</span>
                    </div>
                </div>
            </header>

            {/* Main Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-80px)]">
                {/* Left Column - Upload & Metadata */}
                <div className="lg:col-span-1 flex flex-col gap-6 h-full">
                    {/* File Upload Section */}
                    <div className="h-1/2">
                        <FileUpload onUploadSuccess={handleUploadSuccess} />
                    </div>

                    {/* Metadata Panel Section */}
                    <div className="h-1/2">
                        <MetadataPanel chunks={retrievedChunks} />
                    </div>
                </div>

                {/* Right Column - Chat */}
                <div className="lg:col-span-2 h-full">
                    <ChatPanel onChunksRetrieved={handleChunksRetrieved} />
                </div>
            </div>

            {/* Footer */}
            <footer className="mt-8 text-center text-dark-500 text-xs">
                <p>
                    Retrieval Augmented Generation with{' '}
                    <span className="text-primary-400 font-semibold">Endee</span> Vector Database
                    <br />
                    Built by <span className="text-primary-400 font-semibold">Shrivas Shripad Nadiger</span> For Endee Labs Assignment
                </p>
            </footer>
        </div>
    );
}

export default App;
