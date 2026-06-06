class Solution{
public:
    vector<int> boundary(TreeNode* root){
        if (!root) return {};
        vector<int> ans;
        if (!root->left && !root->right) { ans.push_back(root->data); return ans; }
        ans.push_back(root->data);

        // left boundary (top-down), exclude leaves
        TreeNode* cur = root->left;
        while (cur && !(cur->left == nullptr && cur->right == nullptr)) {
            ans.push_back(cur->data);
            cur = cur->left ? cur->left : cur->right;
        }

        // leaves left-to-right: pre-order over left subtree then right subtree
        collectLeaves(root->left, ans);
        collectLeaves(root->right, ans);

        // right boundary (top-down), collected then appended in reverse
        vector<int> rb;
        cur = root->right;
        while (cur && !(cur->left == nullptr && cur->right == nullptr)) {
            rb.push_back(cur->data);
            cur = cur->right ? cur->right : cur->left;
        }
        for (int i = (int)rb.size() - 1; i >= 0; --i) ans.push_back(rb[i]);
        return ans;
    }
    void collectLeaves(TreeNode* start, vector<int>& ans){
        if (!start) return;
        vector<TreeNode*> st;
        st.push_back(start);
        while (!st.empty()) {
            TreeNode* n = st.back(); st.pop_back();
            if (n->left == nullptr && n->right == nullptr) { ans.push_back(n->data); }
            else {
                if (n->right) st.push_back(n->right);
                if (n->left) st.push_back(n->left);
            }
        }
    }
};
