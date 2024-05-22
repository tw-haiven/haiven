# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.

header_html = """
<div class="header">
    <div class="left-section">
        <div class="logo">
            <img src="../static/thoughtworks_logo.png" alt="Logo">
        </div>
        <div class="separator"></div>
        <div class="title">Haiven team assistant</div>
    </div>
    <div class="mode-switch">
        <span>Choose your working mode</span>
        <button id="standardMode" class="mode-button">Guided mode</button>
        <button id="advancedMode" class="mode-button">Chat mode</button>
    </div>
</div>
"""

header_styles = """
<style>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    background-color: #083049; /* Dark teal background */
    color: white;
}

.left-section {
    display: flex;
    align-items: center;
}

.logo {
    display: flex;
    align-items: center;
}

.logo img {
    height: 20px;
    margin-right: 10px;
}

.separator {
    width: 1px;
    height: 24px;
    background-color: white;
    margin: 0 15px;
}

.title {
    color: white !important;
    font-size: 16px;
}

.mode-switch {
    display: flex;
    align-items: center;
}

.mode-switch span {
    color: white !important;
    margin-right: 10px;
}

.mode-button {
    border: none;
    padding: 5px 10px !important;
    cursor: pointer;
}

#standardMode {
  background-color: white;
  color: black;
  border-top-left-radius: 15px;
  border-bottom-left-radius: 15px;
}

#advancedMode {
  background-color: #2d2d2d;
  color: grey;
  border-top-right-radius: 15px;
  border-bottom-right-radius: 15px;
}

.mode-button.active {
    background-color: #ff6a6a; /* Active button background */
}
</style>
"""

javascript = """
<script>
document.getElementById('standardMode').addEventListener('click', function() {
    this.classList.add('active');
    document.getElementById('advancedMode').classList.remove('active');
});

document.getElementById('advancedMode').addEventListener('click', function() {
    this.classList.add('active');
    document.getElementById('standardMode').classList.remove('active');
});
</script>
"""
