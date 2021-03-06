import numpy as np
from sklearn.neural_network import MLPClassifier


class NeuralNet:
    def __init__(self, nn_type='reg', hidden_layer_sizes=(5,), activation='relu'):
        self.hidden_layer_size = hidden_layer_sizes
        self.nn_type = nn_type
        self.learning_rate = 1e-3
        self.regularization_rate = 1e-4
        self.activation = activation
        self.tol = 1e-3
        self.max_iter = 300
        self.weighs = []
        self.fitted = 0

    def fit(self, X, y, learning_rate=1e-3, reg='l2', regularization_rate=1e-4, tol=1e-3, max_iter=300, verbose=True):
        self.fitted = True
        self.tol = tol
        self.max_iter = max_iter
        self.learning_rate = learning_rate
        self.regularization_rate = regularization_rate
        # begin
        m, n = X.shape
        out_size = 1
        if y.ndim == 2:
            out_size = y.shape[1]
        self.init_weighs(input_size=n, output_size=out_size)
        error_calculator = self.avg_squared_error
        if 'c' in self.nn_type:
            error_calculator = self.avg_cross_entropy
        for k in range(max_iter):
            history = [X.T] + self.feed_forward(X, return_history=1)
            y_p = history[-1]
            if verbose:
                print(f'iteration {k}, {error_calculator.__name__} = {error_calculator(y, y_p, reg)}')
            n_lay = len(history)
            for i in range(n_lay - 1):
                act_i = np.insert(history[i], [0], 1, axis=0)  # add bias line (1)
                sigma_nxt = history[i + 1] - y_p[0]
                grad = np.dot(sigma_nxt, act_i.T) / m
                grad[:, 1:] += (regularization_rate * (self.weighs[i])[:, 1:]) / m
                self.weighs[i] -= (learning_rate * grad)

    def predict(self, X, prob=0, thresh=0.5):
        self.check_for_error()
        y = self.feed_forward(X, return_history=0)[0].T
        if prob:
            return y
        return np.int32(y >= thresh)

    def score(self, X, y):
        self.check_for_error()

    def feed_forward(self, X, return_history=0):
        # returns the list of layers after feed forward
        self.check_for_error()
        y_p = X.T
        history = []
        for i, w in enumerate(self.weighs):
            y_p = np.dot(w, np.insert(y_p, [0], 1, axis=0))
            if i < (len(self.weighs) - 1):
                y_p = self.activate(y_p)
                if return_history:
                    history.append(y_p)
        if 'c' in self.nn_type:  # classifier
            if y_p.shape[0] == 1:
                y_p = self.sig(y_p)
        if return_history:
            history.append(y_p)
            return history
        return y_p

    def init_weighs(self, input_size, output_size):
        # Xavier init weighs if 'tanh' activation and He if 'ReLu'
        layer_sizes = [input_size] + list(self.hidden_layer_size) + [output_size]
        n_layer = len(layer_sizes)
        # special weighs init
        c = 2  # He init
        if self.activation == 'tanh':  # Xavier init
            c = 1
        cf = lambda x: np.sqrt(c / x)
        for i in range(n_layer - 1):
            n_rows = layer_sizes[i + 1]
            n_cols = layer_sizes[i] + 1
            w = np.random.randn(n_rows, n_cols - 1) * cf(n_cols - 1)
            w = np.insert(w, [0], 1, axis=1)
            self.weighs.append(w)

    def avg_cross_entropy(self, y, y_p, reg='l2'):
        # compute cross entropy error with regularization rate (l1 or l2)
        ce = -np.sum(y * np.log(y_p)) - np.sum((1 - y) * np.log(1 - y_p))  # average cross entropy
        regularizator = self.compute_regularization_rate(reg)
        return (ce + regularizator) / len(y)

    def avg_squared_error(self, y, y_p, reg='l2'):
        sqr_error = np.sum((y_p - y) ** 2)
        regularizator = self.compute_regularization_rate(reg)
        return (sqr_error + regularizator) / len(y)

    def compute_regularization_rate(self, reg='l2'):
        regularizator = 0
        if reg == 'l2':
            for w in self.weighs:
                regularizator += np.sum(w[:, 1:] ** 2)
            regularizator *= (self.regularization_rate / 2)
        else:  # l1
            for w in self.weighs:
                regularizator += np.sum(np.abs(w[:, 1:]))
            regularizator *= self.regularization_rate
        return regularizator

    def check_for_error(self):
        # predict the output for the matrix of inputs
        if not self.fitted:
            raise RuntimeError('Model not fitted yet!')

    def activate(self, layer):
        f = getattr(self, self.activation)
        return f(layer)

    @staticmethod
    def sig(matrix):
        return 1 / (1 + np.exp(-matrix))

    @staticmethod
    def relu(matrix):
        matrix[matrix <= 0] = 0
        return matrix

    @staticmethod
    def tanh(matrix):
        tmp = np.exp(-2 * matrix)
        return (1 - tmp) / (1 + tmp)


X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 1, 1, 0])

model = NeuralNet(nn_type='class', hidden_layer_sizes=(1, 1), activation='sig')
model.fit(X, y, learning_rate=0.0001, regularization_rate=0, verbose=1, max_iter=500000)

print(model.predict(X, prob=1))
