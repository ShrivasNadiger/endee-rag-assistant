import React, { useState } from 'react';
import { ingestDocuments } from '../api';

const FileUpload = ({ onUploadSuccess }) => {
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState(null);

    const handleFileInput = (e) => {
        setFiles((prev) => [...prev, ...Array.from(e.target.files)]);
    };

    const removeFile = (index) => {
        setFiles((prev) => prev.filter((_, i) => i !== index));
    };

    const handleUpload = async () => {
        if (!files.length) {
            setUploadStatus({
                type: 'error',
                message: 'Please select at least one file.',
            });
            return;
        }

        setUploading(true);
        setUploadStatus(null);

        try {
            const result = await ingestDocuments(files);
            setUploadStatus({
                type: 'success',
                message: `Processed ${result.files_processed} files • ${result.vectors_stored} vectors • ${result.upsert_time_ms} ms`,
            });
            setFiles([]);
            onUploadSuccess?.(result);
        } catch (err) {
            setUploadStatus({
                type: 'error',
                message:
                    err.response?.data?.detail || 'Upload failed. Please try again.',
            });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="glass-panel p-3 h-full flex flex-col gap-2">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-sm font-semibold text-primary-200">
                        Upload Documents
                    </h2>
                    <p className="text-[11px] text-dark-400 opacity-70">
                        .pdf and .doc/.docx allowed
                    </p>
                </div>

                {/* Plus Button */}
                <label className="w-7 h-7 flex items-center justify-center rounded-full bg-primary-400/20 text-primary-100 hover:bg-primary-500/30 cursor-pointer transition">
                    +
                    <input
                        type="file"
                        multiple
                        accept=".pdf,.doc,.docx"
                        onChange={handleFileInput}
                        className="hidden"
                    />
                </label>
            </div>

            {/* Selected Files */}
            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                {files.length === 0 ? (
                    <div className="text-xs text-dark-500 italic mt-4 text-center">
                        No files selected
                    </div>
                ) : (
                    files.map((file, index) => (
                        <div
                            key={index}
                            className="flex items-center justify-between bg-dark-700/60 border border-dark-600 rounded-md p-2"
                        >
                            <div className="min-w-0">
                                <p className="text-xs text-dark-100 truncate">
                                    {file.name}
                                </p>
                                <p className="text-[10px] text-dark-400">
                                    {(file.size / 1024).toFixed(1)} KB
                                </p>
                            </div>

                            <button
                                onClick={() => removeFile(index)}
                                className="text-red-400 hover:text-red-300 transition"
                                title="Remove file"
                            >
                                ✕
                            </button>
                        </div>
                    ))
                )}
            </div>

            {/* Upload Button */}
            <button
                onClick={handleUpload}
                disabled={uploading || !files.length}
                className="btn-primary w-full text-sm"
            >
                {uploading ? 'Processing…' : 'Upload & Process'}
            </button>

            {/* Status Message */}
            {uploadStatus && (
                <div
                    className={`text-xs p-2 rounded border break-words ${uploadStatus.type === 'success'
                        ? 'bg-green-500/10 border-green-500/30 text-green-200'
                        : 'bg-red-500/10 border-red-500/30 text-red-200'
                        }`}
                >
                    {uploadStatus.message}
                </div>
            )}
        </div>
    );
};

export default FileUpload;
