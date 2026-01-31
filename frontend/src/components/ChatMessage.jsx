import { User, Bot } from 'lucide-react'
import { motion } from 'framer-motion'
import './ChatMessage.css'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export default function ChatMessage({ message, index }) {
    const isUser = message.role === 'user'

    return (
        <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{
                type: "spring",
                stiffness: 260,
                damping: 20,
                delay: index * 0.05
            }}
            className={`chat-message ${isUser ? 'user-message' : 'assistant-message'}`}
        >
            <div className="message-avatar">
                {isUser ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className="message-content">
                <div className="message-header">
                    <span className="message-role">{isUser ? 'You' : 'AI Assistant'}</span>
                    <span className="message-time">
                        {new Date(message.created_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit'
                        })}
                    </span>
                </div>
                <div className="message-text">
                    {isUser ? (
                        message.message
                    ) : (
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                                code({ node, inline, className, children, ...props }) {
                                    return !inline ? (
                                        <div className="code-block-wrapper">
                                            <code className={className} {...props}>
                                                {children}
                                            </code>
                                        </div>
                                    ) : (
                                        <code className={className} {...props}>
                                            {children}
                                        </code>
                                    )
                                }
                            }}
                        >
                            {message.message}
                        </ReactMarkdown>
                    )}
                </div>
            </div>
        </motion.div>
    )
}
