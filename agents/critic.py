from keras import layers, models, optimizers,regularizers
from keras import backend as K

class Critic:
    """Critic (Value) Model."""

    def __init__(self, state_size, action_size):
        """Initialize parameters and build model.

        Params
        ======
            state_size (int): Dimension of each state
            action_size (int): Dimension of each action
        """
        self.state_size = state_size
        self.action_size = action_size

        # Initialize any other variables here

        self.build_model()

    def build_model(self):
        """Build a critic (value) network that maps (state, action) pairs -> Q-values."""
        # Define input layers
        states = layers.Input(shape=(self.state_size,), name='states')
        norm_stat = layers.BatchNormalization()(states)
        actions = layers.Input(shape=(self.action_size,), name='actions')
        norm_act = layers.BatchNormalization()(actions)

        # Add hidden layer(s) for state pathway
        net_states = layers.Dense(units=32, activation='relu')(norm_stat)
        net_states = layers.Dropout(0.3)(net_states)
        net_states = layers.Dense(units=64, activation='relu', kernel_regularizer=regularizers.l2(0.01))(net_states)
        net_states = layers.Dropout(0.3)(net_states)
        norm_stat = layers.BatchNormalization()(net_states)

        # Add hidden layer(s) for action pathway
        net_actions = layers.Dense(units=32, activation='relu')(norm_act)
        net_actions = layers.Dropout(0.3)(net_actions)
        net_actions = layers.Dense(units=64, activation='relu', kernel_regularizer=regularizers.l2(0.01))(net_actions)
        net_actions = layers.Dropout(0.3)(net_actions)
        norm_act = layers.BatchNormalization()(net_actions)

        # Try different layer sizes, activations, add batch normalization, regularizers, etc.

        # Combine state and action pathways
        net = layers.Add()([net_states, net_actions])
        net = layers.Activation('relu')(net)
        net = layers.Dropout(0.3)(net)
        
        net = layers.Dense(units = 10 ,activation = 'relu')(net)
        
        # Add final output layer to prduce action values (Q values)
        Q_values = layers.Dense(units=1, name='q_values')(net)

        # Create Keras model
        self.model = models.Model(inputs=[states, actions], outputs=Q_values)

        # Define optimizer and compile model for training with built-in loss function
        optimizer = optimizers.adam()#RMSprop(lr=0.001, rho=0.9, epsilon=None, decay=1e-6)
        self.model.compile(optimizer=optimizer, loss='mse')

        # Compute action gradients (derivative of Q values w.r.t. to actions)
        action_gradients = K.gradients(Q_values, actions)

        # Define an additional function to fetch action gradients (to be used by actor model)
        self.get_action_gradients = K.function(
            inputs=[*self.model.input, K.learning_phase()],
            outputs=action_gradients)