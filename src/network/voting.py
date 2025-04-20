import time
from flask import jsonify

class Vote:
    def __init__(self, voter, candidate):
        self.voter = voter
        self.candidate = candidate
        self.timestamp = time.time()

    def to_dict(self):
        return {
            'voter': self.voter,
            'candidate': self.candidate,
            'timestamp': self.timestamp
        }

# Store voted users to prevent double voting
voted_users = set()

def setup_voting_routes(app, blockchain, client_logger):
    """
    Setup voting-related routes for the Flask app.
    
    Args:
        app: Flask application instance
        blockchain: Blockchain instance
        client_logger: Logger instance
    """
    @app.route('/vote', methods=['POST'])
    def vote():
        """
        Submit a new vote.
        
        Request body:
        {
            "voter": str,  # Voter's ID
            "candidate": str  # Candidate's ID
        }
        
        Returns:
            JSON response with status and transaction details
        """
        try:
            data = request.get_json()
            voter = data.get('voter')
            candidate = data.get('candidate')

            if not voter or not candidate:
                return jsonify({
                    'status': 'error',
                    'message': 'Missing required parameters'
                }), 400

            # Check if user has already voted
            if voter in voted_users:
                return jsonify({
                    'status': 'error',
                    'message': 'User has already voted'
                }), 400

            # Create voting transaction
            transaction = {
                'sender': voter,
                'recipient': candidate,
                'amount': 1  # Each vote counts as 1
            }

            # Add to pending transactions
            blockchain.add_transaction(transaction)
            voted_users.add(voter)

            client_logger.info(f"User {voter} voted for {candidate}")

            return jsonify({
                'status': 'success',
                'message': 'Vote submitted successfully',
                'data': {
                    'transaction': transaction
                }
            })

        except Exception as e:
            client_logger.error(f"Vote submission failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Vote submission failed: {str(e)}'
            }), 500

    @app.route('/votes', methods=['GET'])
    def get_votes():
        """
        Get voting results for all candidates.
        
        Returns:
            JSON response with vote counts and total votes
        """
        try:
            # Count votes for each candidate
            vote_counts = {}
            for block in blockchain.chain:
                for transaction in block.transactions:
                    if transaction['amount'] == 1:
                        candidate = transaction['recipient']
                        vote_counts[candidate] = vote_counts.get(candidate, 0) + 1

            # Convert to list format
            results = [
                {
                    'candidate': candidate,
                    'votes': count
                }
                for candidate, count in vote_counts.items()
            ]

            total_votes = sum(vote_counts.values())

            return jsonify({
                'status': 'success',
                'data': {
                    'results': results,
                    'total_votes': total_votes,
                    'last_updated': time.time()
                }
            })

        except Exception as e:
            client_logger.error(f"Failed to get voting results: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to get voting results: {str(e)}'
            }), 500

    @app.route('/vote_status', methods=['GET'])
    def get_vote_status():
        """
        Get voting status for a specific user.
        
        Query parameters:
        - voter: str  # User's ID
        
        Returns:
            JSON response with user's voting status and details
        """
        try:
            voter = request.args.get('voter')
            if not voter:
                return jsonify({
                    'status': 'error',
                    'message': 'Missing voter ID'
                }), 400

            # Check if user has voted
            has_voted = voter in voted_users
            voted_candidate = None
            vote_time = None
            block_height = None

            if has_voted:
                # Find user's vote in blockchain
                for block in reversed(blockchain.chain):
                    for transaction in block.transactions:
                        if transaction['sender'] == voter and transaction['amount'] == 1:
                            voted_candidate = transaction['recipient']
                            vote_time = block.timestamp
                            block_height = block.index
                            break
                    if voted_candidate:
                        break

            return jsonify({
                'status': 'success',
                'data': {
                    'voter': voter,
                    'has_voted': has_voted,
                    'voted_candidate': voted_candidate,
                    'vote_time': vote_time,
                    'block_height': block_height
                }
            })

        except Exception as e:
            client_logger.error(f"Failed to get vote status: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to get vote status: {str(e)}'
            }), 500

    @app.route('/candidates', methods=['GET'])
    def get_candidates():
        """
        Get list of all candidates and their vote counts.
        
        Returns:
            JSON response with list of candidates and their statistics
        """
        try:
            # Get all unique candidates from blockchain
            candidates = set()
            vote_counts = {}
            
            for block in blockchain.chain:
                for transaction in block.transactions:
                    if transaction['amount'] == 1:
                        candidate = transaction['recipient']
                        candidates.add(candidate)
                        vote_counts[candidate] = vote_counts.get(candidate, 0) + 1

            # Calculate total votes
            total_votes = sum(vote_counts.values())
            
            # Prepare response
            candidates_list = []
            for candidate in sorted(candidates):
                votes = vote_counts.get(candidate, 0)
                percentage = (votes / total_votes * 100) if total_votes > 0 else 0
                
                candidates_list.append({
                    'candidate': candidate,
                    'votes': votes,
                    'percentage': round(percentage, 2)
                })

            return jsonify({
                'status': 'success',
                'data': {
                    'candidates': candidates_list,
                    'total_votes': total_votes,
                    'last_updated': time.time()
                }
            })

        except Exception as e:
            client_logger.error(f"Failed to get candidates list: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to get candidates list: {str(e)}'
            }), 500

    @app.route('/voter_stats', methods=['GET'])
    def get_voter_stats():
        """
        Get voting statistics including voter participation rate.
        
        Returns:
            JSON response with voting statistics
        """
        try:
            # Get all unique voters
            voters = set()
            total_votes = 0
            
            for block in blockchain.chain:
                for transaction in block.transactions:
                    if transaction['amount'] == 1:
                        voter = transaction['sender']
                        voters.add(voter)
                        total_votes += 1

            # Get current voted users
            current_voters = len(voted_users)
            
            # Calculate participation rate
            participation_rate = (current_voters / len(voters) * 100) if len(voters) > 0 else 0
            
            # Get vote distribution by time
            vote_timeline = {}
            for block in blockchain.chain:
                for transaction in block.transactions:
                    if transaction['amount'] == 1:
                        timestamp = block.timestamp
                        hour = time.strftime('%Y-%m-%d %H:00', time.localtime(timestamp))
                        vote_timeline[hour] = vote_timeline.get(hour, 0) + 1

            return jsonify({
                'status': 'success',
                'data': {
                    'total_voters': len(voters),
                    'current_voters': current_voters,
                    'participation_rate': round(participation_rate, 2),
                    'total_votes': total_votes,
                    'vote_timeline': vote_timeline,
                    'last_updated': time.time()
                }
            })

        except Exception as e:
            client_logger.error(f"Failed to get voter statistics: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to get voter statistics: {str(e)}'
            }), 500 