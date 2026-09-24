import streamlit as st

st.set_page_config(
    page_title="AI Incident Management",
    page_icon="🚨",
    layout="wide",
)

st.title("🚨 AI Incident Management Platform")

st.info(
    """
    **Phase 1: Foundation Complete**
    
    The frontend dashboard will be fully implemented in Phase 4.
    
    Current Status:
    - ✅ Database models configured
    - ✅ FastAPI foundation ready
    - ✅ Environment setup complete
    - ⏳ Authentication (Phase 2)
    - ⏳ CRUD endpoints (Phase 2)
    - ⏳ RAG engine (Phase 3)
    - ⏳ Full UI implementation (Phase 4)
    """
)

st.header("🔗 Quick Links")
col1, col2, col3 = st.columns(3)

with col1:
    st.write(
        """
        **API Documentation**
        
        [Swagger UI](http://localhost:8000/docs)
        
        [ReDoc](http://localhost:8000/redoc)
        """
    )

with col2:
    st.write(
        """
        **Health Checks**
        
        [Backend Health](http://localhost:8000/health)
        
        [Ollama Status](http://localhost:11434/api/tags)
        """
    )

with col3:
    st.write(
        """
        **Documentation**
        
        [README](../README.md)
        
        [GitHub](https://github.com)
        """
    )

st.markdown("---")
st.success("✅ Frontend container is running. Phase 1 setup complete!")