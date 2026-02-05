import React from 'react';

const MetadataPanel = ({ chunks }) => {
    if (!chunks || chunks.length === 0) {
        return (
            <div className="glass-panel p-6 h-full flex items-center justify-center">
                <div className="text-center text-dark-400">
                    <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-sm">No retrieved chunks yet</p>
                    <p className="text-xs mt-2">Ask a question to see retrieved documents</p>
                </div>
            </div>
        );
    }

    return (
        <div className="glass-panel p-6 h-full flex flex-col">
            <h2 className="text-xl font-bold mb-4 text-primary-400 flex items-center gap-2">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Retrieved Chunks
                <span className="metric-badge ml-auto">{chunks.length} chunks</span>
            </h2>

            <div className="flex-1 overflow-y-auto space-y-3">
                {chunks.map((chunk, index) => (
                    <div
                        key={chunk.id || index}
                        className="bg-dark-700/50 rounded-lg p-4 border border-dark-600 hover:border-primary-500/50 transition-all"
                    >
                        {/* Header */}
                        <div className="flex items-start justify-between mb-3">
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    <svg className="w-4 h-4 text-primary-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                    </svg>
                                    <h3 className="text-sm font-semibold text-dark-100 truncate">
                                        {chunk.document_name || 'Unknown Document'}
                                    </h3>
                                </div>

                                {/* Location Info */}
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {chunk.page_number && (
                                        <span className="inline-flex items-center px-2 py-1 rounded bg-primary-500/10 text-primary-300 text-xs border border-primary-500/20">
                                            <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                            </svg>
                                            Page {chunk.page_number}
                                        </span>
                                    )}

                                    {chunk.paragraph_index && (
                                        <span className="inline-flex items-center px-2 py-1 rounded bg-primary-500/10 text-primary-300 text-xs border border-primary-500/20">
                                            <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
                                            </svg>
                                            Para {chunk.paragraph_index}
                                        </span>
                                    )}

                                    <span className="inline-flex items-center px-2 py-1 rounded bg-dark-600 text-dark-300 text-xs">
                                        Chunk #{chunk.chunk_index}
                                    </span>
                                </div>
                            </div>

                            {/* Similarity Score */}
                            <div className="ml-3 flex-shrink-0">
                                <div className="text-right">
                                    <div className="text-xs text-dark-400 mb-1">Similarity</div>
                                    <div className="text-sm font-bold text-primary-400">
                                        {(chunk.similarity * 100).toFixed(1)}%
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Chunk ID */}
                        <div className="mb-2">
                            <span className="text-xs text-dark-500">ID: </span>
                            <code className="text-xs text-dark-400 bg-dark-800/50 px-2 py-1 rounded font-mono">
                                {chunk.id}
                            </code>
                        </div>

                        {/* Text Preview */}
                        {chunk.text && (
                            <div className="mt-3 pt-3 border-t border-dark-600">
                                <p className="text-xs text-dark-300 line-clamp-3">
                                    {chunk.text}
                                </p>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MetadataPanel;
