import React, { useState } from 'react';
import './BetGames.css'; // Add necessary CSS for styling modal
import TopForm from '../TopForm/TopForm';

const BetGames = ({title}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [amount, setAmount] = useState('');
    const [odds, setOdds] = useState('');

    const openModal = () => {
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
    };

    const handleAmountChange = (event) => {
        setAmount(event.target.value);
    };

    const handleOddsChange = (event) => {
        setOdds(event.target.value);
    };

    const handleSubmit = () => {
        console.log('Submitted: Amount -', amount, ' Odds -', odds);
        setAmount('');
        setOdds('');
        closeModal();
    };

    return (
        <div className="button-and-modal">
            <button className="bet-button" onClick={openModal}>BET</button>
            {isModalOpen && (

                <div className='modal'> 
                    <TopForm
                        title={title}
                        showCloseButton={true}
                        onClose={closeModal}
                    >
                        <form onSubmit={handleSubmit}>
                            <input
                                type="text"
                                placeholder="Wager"
                                value={amount}
                                onChange={handleAmountChange}
                            />
                            <input
                                type="text"
                                placeholder="Odds"
                                value={odds}
                                onChange={handleOddsChange}
                            />
                            <button type="submit" className='select-button' style={{ marginTop: '10px' }}>
                                Place Bet
                            </button>
                        </form>
                    </TopForm>
                </div>
                    
            )}
        </div>
    );
}

export default BetGames;
