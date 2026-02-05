import React, { useState, useRef, useEffect } from 'react';
import { queryRAG } from '../api';

const ChatPanel = ({ onChunksRetrieved }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!input.trim() || loading) return;

        const userMessage = {
            role: 'user',
            content: input.trim(),
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const result = await queryRAG(input.trim());

            const assistantMessage = {
                role: 'assistant',
                content: result.answer,
                chunks: result.chunks,
                retrieval_latency_ms: result.retrieval_latency_ms,
                generation_latency_ms: result.generation_latency_ms,
                total_latency_ms: result.total_latency_ms,
                timestamp: new Date().toISOString(),
            };

            setMessages((prev) => [...prev, assistantMessage]);

            // Update metadata panel
            if (onChunksRetrieved) {
                onChunksRetrieved(result.chunks);
            }
        } catch (error) {
            const errorMessage = {
                role: 'error',
                content: error.response?.data?.detail || 'Failed to get response. Please try again.',
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const formatAnswer = (text) => {
        // Split text into parts (text and citations)
        const parts = [];
        const regex = /\[([^\]]+)\]/g;
        let lastIndex = 0;
        let match;

        while ((match = regex.exec(text)) !== null) {
            // Add text before citation
            if (match.index > lastIndex) {
                parts.push({
                    type: 'text',
                    content: text.substring(lastIndex, match.index),
                });
            }

            // Add citation
            parts.push({
                type: 'citation',
                content: match[1],
            });

            lastIndex = match.index + match[0].length;
        }

        // Add remaining text
        if (lastIndex < text.length) {
            parts.push({
                type: 'text',
                content: text.substring(lastIndex),
            });
        }

        return parts;
    };

    return (
        <div className="glass-panel p-6 h-full flex flex-col">
            <h2 className="text-xl font-bold mb-4 text-primary-400 flex items-center gap-2">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                RAG Chat
            </h2>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto mb-4 space-y-4">
                {messages.length === 0 && (
                    <div className="h-full flex items-center justify-center">
                        <div className="text-center text-dark-400">
                            <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                            <p className="text-sm">Start a conversation</p>
                            <p className="text-xs mt-2">Ask questions about your uploaded documents</p>
                        </div>
                    </div>
                )}

                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[85%] rounded-lg p-4 ${message.role === 'user'
                                    ? 'bg-primary-600 text-white'
                                    : message.role === 'error'
                                        ? 'bg-red-500/20 border border-red-500/30 text-red-300'
                                        : 'bg-dark-700/70 border border-dark-600 text-dark-100'
                                }`}
                        >
                            {message.role === 'assistant' ? (
                                <>
                                    {/* Answer with Citations */}
                                    <div className="mb-3 leading-relaxed">
                                        {formatAnswer(message.content).map((part, idx) => (
                                            part.type === 'citation' ? (
                                                <span key={idx} className="citation">
                                                    {part.content}
                                                </span>
                                            ) : (
                                                <span key={idx}>{part.content}</span>
                                            )
                                        ))}
                                    </div>

                                    {/* Latency Metrics */}
                                    <div className="pt-3 border-t border-dark-600 flex flex-wrap gap-2 text-xs">
                                        <div className="metric-badge">
                                            <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                            </svg>
                                            Endee Retrieval: {message.retrieval_latency_ms}ms
                                        </div>
                                        <div className="metric-badge">
                                            <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                            </svg>
                                            Generation: {message.generation_latency_ms}ms
                                        </div>
                                        <div className="metric-badge">
                                            <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            Total: {message.total_latency_ms}ms
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <p className="leading-relaxed">{message.content}</p>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-dark-700/70 border border-dark-600 rounded-lg p-4">
                            <div className="flex items-center gap-2 text-dark-300">
                                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span className="text-sm">Searching and generating answer...</span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask a question about your documents..."
                    className="input-field flex-1"
                    disabled={loading}
                />
                <button
                    type="submit"
                    disabled={loading || !input.trim()}
                    className="btn-primary px-6"
                >
                    {loading ? (
                        <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    ) : (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                    )}
                </button>
            </form>
        </div>
    );
};

export default ChatPanel;
